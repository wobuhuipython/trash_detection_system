import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal
from collections import deque
import numpy as np
import torch


class WebcamWorker(QThread):
    frame_ready = pyqtSignal(object)  # 原始帧
    result_ready = pyqtSignal(object)  # 检测结果帧
    detection_complete = pyqtSignal(object)

    def __init__(self, model, conf_threshold=0.4):
        super().__init__()
        self.model = model
        self.conf_threshold = conf_threshold
        self.running = True
        
        # 模型参数
        self.target_size = (640, 640)  # YOLO默认输入尺寸
        self.padding_color = (114, 114, 114)  # 标准填充色
        
        # 摄像头初始化
        self.cap = self._init_camera()
        self.frame_buffer = deque(maxlen=1)
        
        # 检测稳定性
        self.detection_history = deque(maxlen=5)
        self.require_frames = 2  # 需要连续出现的帧数
        
        # 保持固定输出尺寸
        self.output_size = (640, 640)

    def _init_camera(self):
        """摄像头初始化配置，支持多索引与多后端回退"""
        preferred_backends = [getattr(cv2, 'CAP_DSHOW', 700), getattr(cv2, 'CAP_MSMF', 1400), getattr(cv2, 'CAP_ANY', 0)]
        candidate_indices = [0, 1, 2, 3, 4, 5]

        last_error = None
        for idx in candidate_indices:
            for backend in preferred_backends:
                try:
                    cap = cv2.VideoCapture(idx, backend)
                    if cap is not None and cap.isOpened():
                        # 基本属性设置（尽量容错，不因失败中断）
                        try:
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            cap.set(cv2.CAP_PROP_FPS, 30)
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            # 某些设备不支持该属性，忽略返回值
                            _ = cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                            
                            # 曝光控制设置 - 解决曝光问题
                            # 关闭自动曝光
                            _ = cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25表示手动曝光
                            # 设置固定曝光值（根据环境调整，-13到-1之间）
                            _ = cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # 中等曝光值
                            # 设置固定增益（减少噪点）
                            _ = cap.set(cv2.CAP_PROP_GAIN, 0)  # 最小增益
                            # 设置白平衡为自动
                            _ = cap.set(cv2.CAP_PROP_AUTO_WB, 1)
                        except Exception:
                            pass
                        return cap
                    if cap is not None:
                        cap.release()
                except Exception as e:
                    last_error = e
                    try:
                        if 'cap' in locals() and cap is not None:
                            cap.release()
                    except Exception:
                        pass

        raise RuntimeError("无法打开摄像头：请检查设备连接与权限。{}".format(f" 详情: {last_error}" if last_error else ""))

    def _yolo_preprocess(self, frame):
        """YOLO标准预处理流程 - CPU版本"""
        # 1. 保持宽高比缩放
        h, w = frame.shape[:2]
        scale = min(self.target_size[0]/h, self.target_size[1]/w)
        resized = cv2.resize(frame, None, fx=scale, fy=scale, 
                           interpolation=cv2.INTER_LINEAR)
        
        # 2. 边缘填充
        pad_h = self.target_size[0] - resized.shape[0]
        pad_w = self.target_size[1] - resized.shape[1]
        padded = cv2.copyMakeBorder(
            resized,
            top=pad_h//2,
            bottom=pad_h - pad_h//2,
            left=pad_w//2,
            right=pad_w - pad_w//2,
            borderType=cv2.BORDER_CONSTANT,
            value=self.padding_color
        )
        
        # 3. 转换为RGB并归一化
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb.astype(np.float32) / 255.0)
        
        # 4. 调整维度顺序，保持在CPU
        return tensor.permute(2, 0, 1).unsqueeze(0)

    def run(self):
        # 启动独立的采集线程
        from threading import Thread
        Thread(target=self._capture_thread, daemon=True).start()
        
        while self.running:
            if len(self.frame_buffer) == 0:
                time.sleep(0.001)
                continue
                
            frame = self.frame_buffer.popleft()
            # 先调整到固定输出尺寸，避免后续处理导致尺寸变化
            display_frame = cv2.resize(frame.copy(), self.output_size)
            
            try:
                # 1. 预处理
                tensor = self._yolo_preprocess(frame)
                
                # 2. 模型推理 - CPU版本
                with torch.no_grad():
                    results = self.model(tensor, conf=self.conf_threshold)
                
                # 发送原始帧到左侧显示区域
                self.frame_ready.emit(display_frame)
                
                # 修正结果处理逻辑
                if len(results) == 0:
                    # 没有检测结果时，右侧也显示原始帧
                    self.result_ready.emit(display_frame)
                    continue
                    
                filtered = self._filter_results(results)
                if not filtered:  # 处理空结果
                    # 没有有效检测结果时，右侧也显示原始帧
                    self.result_ready.emit(display_frame)
                    continue
                    
                # 在固定尺寸的帧上绘制结果，发送到右侧显示区域
                annotated = self._render_results(display_frame, filtered[0], frame)
                self.result_ready.emit(annotated)
                self.detection_complete.emit(filtered)
                
            except Exception as e:
                print(f"[处理错误] {str(e)}")
                self.frame_ready.emit(display_frame)
                self.result_ready.emit(display_frame)

    def _filter_results(self, results):
        """增强的稳定性过滤"""
        if not results or len(results) == 0:
            return []
            
        result = results[0]
        if not hasattr(result, 'boxes') or len(result.boxes) == 0:
            return []
            
        current = result.boxes.data.cpu().numpy()
        self.detection_history.append(current)

        if len(self.detection_history) < self.require_frames:
            return [result]

        # 使用更高效的矩阵运算
        scores = np.zeros(len(current))
        for i, det in enumerate(current):
            scores[i] = sum(
                np.any([self._is_same(det, hist_det) for hist_det in frame_dets])
                for frame_dets in self.detection_history
            )

        mask = scores >= (len(self.detection_history) // 2)
        result.boxes.data = result.boxes.data[mask]
        return [result] if len(result.boxes) > 0 else []

    def _is_same(self, det1, det2, iou_thresh=0.3):
        """更健壮的IOU计算"""
        try:
            box1, box2 = det1[:4], det2[:4]
            cls1, cls2 = int(det1[5]), int(det2[5])
            
            # 类别不同直接返回False
            if cls1 != cls2:
                return False
                
            # 计算IOU
            x1 = max(box1[0], box2[0])
            y1 = max(box1[1], box2[1])
            x2 = min(box1[2], box2[2])
            y2 = min(box1[3], box2[3])
            
            inter = max(0, x2 - x1) * max(0, y2 - y1)
            area1 = (box1[2]-box1[0])*(box1[3]-box1[1])
            area2 = (box2[2]-box2[0])*(box2[3]-box2[1])
            union = area1 + area2 - inter + 1e-6
            
            return (inter / union) > iou_thresh
        except Exception as e:
            print(f"[IOU计算错误] {e}")
            return False

    def _render_results(self, display_frame, result, original_frame):
        """在固定尺寸的帧上绘制检测结果"""
        # 获取原始帧和显示帧的尺寸比例
        orig_h, orig_w = original_frame.shape[:2]
        disp_h, disp_w = display_frame.shape[:2]
        
        # 计算缩放比例
        scale_x = disp_w / orig_w
        scale_y = disp_h / orig_h
        
        # 2. 绘制检测框
        annotated = display_frame.copy()
        for box in result.boxes:
            # 转换到原图坐标
            x1 = (box.xyxy[0][0].item() - self.target_size[1]//2 + orig_w*min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)/2) / min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)
            y1 = (box.xyxy[0][1].item() - self.target_size[0]//2 + orig_h*min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)/2) / min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)
            x2 = (box.xyxy[0][2].item() - self.target_size[1]//2 + orig_w*min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)/2) / min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)
            y2 = (box.xyxy[0][3].item() - self.target_size[0]//2 + orig_h*min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)/2) / min(self.target_size[0]/orig_h, self.target_size[1]/orig_w)
            
            # 应用缩放比例到显示帧
            x1, y1 = int(x1 * scale_x), int(y1 * scale_y)
            x2, y2 = int(x2 * scale_x), int(y2 * scale_y)
            
            # 确保坐标在图像范围内
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(disp_w, x2), min(disp_h, y2)
            
            # 跳过无效检测框
            if x1 >= x2 or y1 >= y2:
                continue
                
            # 绘制半透明框
            overlay = annotated.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0,180,0), -1)
            annotated = cv2.addWeighted(overlay, 0.2, annotated, 0.8, 0)
            
            # 绘制边框和标签
            conf = box.conf.item()  # 显式转换为Python float
            label = f"{self.model.names[int(box.cls)]} {conf:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(annotated, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2, cv2.LINE_AA)
        
        return annotated

    def _capture_thread(self):
        """专用的采集线程"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_buffer.append(frame)
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.wait(500)