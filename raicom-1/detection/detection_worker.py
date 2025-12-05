from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import time
import os
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.history_manager import history_manager

class DetectionWorker(QThread):
    detection_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    record_saved = pyqtSignal(bool, str)  # 新增：记录保存信号

    def __init__(self, model, detection_type, source=None, conf_threshold=0.5, save_to_history=True):
        super().__init__()
        self.model = model
        self.detection_type = detection_type
        self.source = source
        self.conf_threshold = conf_threshold
        self.save_to_history = save_to_history
        self.running = True

    def run(self):
        if self.detection_type == "image":
            self.detect_image()

    def detect_image(self):
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 读取图像
            image = cv2.imread(self.source)
            if image is None:
                self.error_occurred.emit("无法读取图片")
                return
            
            print(f"正在检测图像: {self.source}")
            print(f"图像尺寸: {image.shape}")
            
            # 使用YOLO模型进行预测
            results = self.model.predict(image, conf=self.conf_threshold)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            print(f"检测完成，发现 {len(results[0].boxes)} 个对象")
            print(f"处理时间: {processing_time:.2f}秒")
            
            # 发送检测结果
            self.detection_complete.emit(results)
            
            # 保存检测记录到历史
            if self.save_to_history:
                self.save_detection_record(results, processing_time)
            
        except Exception as e:
            print(f"检测过程中出错: {e}")
            self.error_occurred.emit(f"检测失败: {str(e)}")
    
    def save_detection_record(self, results, processing_time):
        """保存检测记录到历史数据库"""
        try:
            # 提取检测结果
            detection_results = []
            confidence_scores = []
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    box = boxes[i]
                    # 获取类别名称
                    class_id = int(box.cls[0]) if box.cls is not None else 0
                    class_name = self.model.names[class_id] if hasattr(self.model, 'names') else f"Class_{class_id}"
                    
                    # 获取置信度
                    confidence = float(box.conf[0]) if box.conf is not None else 0.0
                    confidence_scores.append(confidence)
                    
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection_result = {
                        'class': class_name,
                        'confidence': confidence,
                        'x': x1,
                        'y': y1,
                        'width': x2 - x1,
                        'height': y2 - y1
                    }
                    detection_results.append(detection_result)
            
            # 生成结果图片
            result_image_path, result_image_data = self.generate_result_image(results)
            
            # 确定来源类型
            source_type = 'upload'  # 图片上传
            
            # 保存到数据库
            success = history_manager.save_detection_record(
                image_path=self.source,
                detection_results=detection_results,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                source_type=source_type,
                result_image_path=result_image_path,
                result_image_data=result_image_data
            )
            
            if success:
                self.record_saved.emit(True, f"检测记录已保存: {os.path.basename(self.source)}")
            else:
                self.record_saved.emit(False, "保存检测记录失败")
                
        except Exception as e:
            print(f"保存检测记录时出错: {e}")
            self.record_saved.emit(False, f"保存记录失败: {str(e)}")
    
    def generate_result_image(self, results):
        """生成带检测框的结果图片"""
        try:
            if not results or len(results) == 0:
                return None, None
            
            # 读取原始图片
            original_image = cv2.imread(self.source)
            if original_image is None:
                return None, None
            
            # 使用YOLO的plot方法生成带标注的图片
            result = results[0]
            if hasattr(result, 'orig_shape'):
                orig_height, orig_width = result.orig_shape
            else:
                orig_height, orig_width = original_image.shape[:2]
            
            # 生成结果图片
            annotated_image = result.plot()
            
            # 转换颜色空间（BGR -> RGB）
            if len(annotated_image.shape) == 3 and annotated_image.shape[2] == 3:
                annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
            
            # 生成结果图片文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(self.source))[0]
            result_filename = f"{base_name}_result_{timestamp}.jpg"
            
            # 创建结果图片目录
            result_dir = os.path.join(os.path.dirname(self.source), "results")
            os.makedirs(result_dir, exist_ok=True)
            result_image_path = os.path.join(result_dir, result_filename)
            
            # 保存结果图片
            cv2.imwrite(result_image_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
            
            # 读取结果图片数据
            with open(result_image_path, 'rb') as f:
                result_image_data = f.read()
            
            return result_image_path, result_image_data
            
        except Exception as e:
            print(f"生成结果图片失败: {e}")
            return None, None