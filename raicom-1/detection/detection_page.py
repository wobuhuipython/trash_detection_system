"""
垃圾检测页面 - 优化版布局
"""
import os
import cv2
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QMessageBox, QTextEdit, 
                             QComboBox, QSlider, QProgressBar, QFrame,
                             QSizePolicy, QCheckBox, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QImage, QPixmap, QColor
from ultralytics import YOLO
from detection.webcam_worker import WebcamWorker
from detection.detection_worker import DetectionWorker
from detection.utils import get_garbage_info
from window.styles import COLORS, GRADIENTS


class DetectionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.model = None
        self.current_results = None
        self.current_image_path = None
        self.worker = None
        self.webcam_worker = None
        self.detection_start_time = None
        self.detection_count = 0
        self.settings = {'output_directory': os.getcwd()}
        self.init_ui()

    def _add_shadow(self, widget, blur=15, offset=3, color=QColor(102, 126, 234, 35)):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_light']};
                font-family: 'Microsoft YaHei', Arial;
            }}
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(10)

        # 工具栏
        self._create_toolbar(main_layout)
        
        # 主内容区
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        self._create_image_panel(content_layout)
        self._create_info_panel(content_layout)
        main_layout.addLayout(content_layout, 1)
        
        # 状态栏
        self._create_footer(main_layout)

    def _create_toolbar(self, parent_layout):
        toolbar = QFrame()
        toolbar.setFixedHeight(55)
        toolbar.setStyleSheet(f"QFrame {{ background: {COLORS['bg_white']}; border: 1px solid {COLORS['border']}; border-radius: 10px; }}")
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)
        
        # 模型选择
        self.model_button = QPushButton("选择模型")
        self.model_button.setFixedSize(100, 36)
        self.model_button.clicked.connect(self.load_model_dialog)
        self._style_button(self.model_button, 'primary')
        layout.addWidget(self.model_button)
        
        # 分隔线
        layout.addWidget(self._create_separator())
        
        # 检测模式
        mode_label = QLabel("模式:")
        mode_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_light']};")
        layout.addWidget(mode_label)
        
        self.detect_type_combo = QComboBox()
        self.detect_type_combo.addItems(["图片检测", "摄像头检测"])
        self.detect_type_combo.setFixedSize(110, 36)
        self.detect_type_combo.currentIndexChanged.connect(self.on_detect_type_changed)
        self._style_combo(self.detect_type_combo)
        layout.addWidget(self.detect_type_combo)
        
        # 分隔线
        layout.addWidget(self._create_separator())
        
        # 置信度
        conf_label = QLabel("置信度:")
        conf_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_light']};")
        layout.addWidget(conf_label)
        
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(1, 99)
        self.conf_slider.setValue(50)
        self.conf_slider.setFixedWidth(100)
        self.conf_slider.valueChanged.connect(self.update_conf_threshold)
        self._style_slider(self.conf_slider)
        layout.addWidget(self.conf_slider)
        
        self.conf_value_label = QLabel("0.50")
        self.conf_value_label.setFixedWidth(35)
        self.conf_value_label.setAlignment(Qt.AlignCenter)
        self.conf_value_label.setStyleSheet(f"background: {COLORS['primary']}; color: white; border-radius: 4px; font-size: 11px; font-weight: bold;")
        layout.addWidget(self.conf_value_label)
        
        layout.addStretch()
        
        # 自动保存
        self.auto_save_check = QCheckBox("自动保存")
        self.auto_save_check.setChecked(True)
        self.auto_save_check.setStyleSheet(f"""
            QCheckBox {{ font-size: 12px; color: {COLORS['text_dark']}; spacing: 5px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; border: 2px solid {COLORS['border']}; }}
            QCheckBox::indicator:checked {{ background: {COLORS['success']}; border-color: {COLORS['success']}; }}
        """)
        layout.addWidget(self.auto_save_check)
        
        # 检测按钮
        self.detect_button = QPushButton("开始检测")
        self.detect_button.setFixedSize(100, 36)
        self.detect_button.clicked.connect(self.start_detection)
        self._style_button(self.detect_button, 'success')
        layout.addWidget(self.detect_button)
        
        # 摄像头按钮
        self.cam_buttons_widget = QWidget()
        cam_layout = QHBoxLayout(self.cam_buttons_widget)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_layout.setSpacing(6)
        self.start_cam_button = QPushButton("启动")
        self.start_cam_button.setFixedSize(60, 36)
        self.start_cam_button.clicked.connect(self.start_webcam)
        self._style_button(self.start_cam_button, 'success')
        cam_layout.addWidget(self.start_cam_button)
        self.stop_cam_button = QPushButton("停止")
        self.stop_cam_button.setFixedSize(60, 36)
        self.stop_cam_button.clicked.connect(self.stop_webcam)
        self._style_button(self.stop_cam_button, 'danger')
        cam_layout.addWidget(self.stop_cam_button)
        self.cam_buttons_widget.hide()
        layout.addWidget(self.cam_buttons_widget)
        
        # 历史记录
        self.history_btn = QPushButton("历史记录")
        self.history_btn.setFixedSize(80, 36)
        self.history_btn.clicked.connect(self.go_to_history)
        self._style_button(self.history_btn, 'primary')
        layout.addWidget(self.history_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(80, 6)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"QProgressBar {{ border: none; border-radius: 3px; background: {COLORS['bg_light']}; }} QProgressBar::chunk {{ background: {GRADIENTS['primary']}; border-radius: 3px; }}")
        layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(toolbar)

    def _create_image_panel(self, parent_layout):
        """创建图像显示区域"""
        # 左侧卡片
        image_card = QFrame()
        image_card.setStyleSheet(f"""
            QFrame {{ 
                background: white; 
                border: 1px solid {COLORS['border']}; 
                border-radius: 10px; 
            }}
        """)
        
        layout = QVBoxLayout(image_card)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        # 标题行
        title_row = QHBoxLayout()
        title = QLabel("检测结果")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_dark']};")
        title_row.addWidget(title)
        title_row.addStretch()
        self.image_info_label = QLabel("")
        self.image_info_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_light']};")
        title_row.addWidget(self.image_info_label)
        layout.addLayout(title_row)
        
        # 图像显示区域
        self.result_label = QLabel("点击「开始检测」选择图片")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_label.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['bg_light']};
                border: 2px dashed {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_light']};
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.result_label, 1)
        
        parent_layout.addWidget(image_card, 7)

    def _create_info_panel(self, parent_layout):
        """创建信息面板"""
        # 右侧卡片
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{ 
                background: white; 
                border: 1px solid {COLORS['border']}; 
                border-radius: 10px; 
            }}
        """)
        
        layout = QVBoxLayout(info_card)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel("检测信息")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        # 统计区
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)
        
        self.target_count_label = self._create_stat_item("0", "目标", COLORS['primary'])
        stats_layout.addWidget(self.target_count_label)
        self.avg_conf_label = self._create_stat_item("--", "置信度", COLORS['success'])
        stats_layout.addWidget(self.avg_conf_label)
        self.time_label = self._create_stat_item("--", "耗时", COLORS['warning'])
        stats_layout.addWidget(self.time_label)
        layout.addLayout(stats_layout)
        
        # 详细信息
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: {COLORS['text_dark']};
            }}
        """)
        self.info_text.setPlaceholderText("等待检测...")
        layout.addWidget(self.info_text, 1)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.clicked.connect(self._reset_display)
        self._style_small_button(self.clear_btn, 'danger')
        btn_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("导出")
        self.export_btn.setFixedHeight(34)
        self.export_btn.clicked.connect(self.export_result)
        self._style_small_button(self.export_btn, 'primary')
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)
        
        parent_layout.addWidget(info_card, 3)

    def _create_stat_item(self, value, label, color):
        item = QFrame()
        item.setFixedHeight(58)
        item.setStyleSheet(f"""
            QFrame {{ 
                background: {COLORS['bg_light']}; 
                border-radius: 8px; 
                border: none;
            }}
        """)
        layout = QVBoxLayout(item)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: bold; 
            color: {color}; 
            background: transparent;
        """)
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"""
            font-size: 11px; 
            color: {COLORS['text_light']}; 
            background: transparent;
        """)
        layout.addWidget(text_label)
        return item

    def _create_footer(self, parent_layout):
        footer = QFrame()
        footer.setFixedHeight(38)
        footer.setStyleSheet(f"""
            QFrame {{ 
                background: {COLORS['bg_white']}; 
                border: 1px solid {COLORS['border']}; 
                border-radius: 10px; 
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(15)
        
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")
        layout.addWidget(self.status_dot)
        
        self.status_label = QLabel("系统就绪")
        self.status_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_dark']}; font-weight: 500;")
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # 分隔符样式
        sep_style = f"color: {COLORS['border']}; font-size: 12px;"
        info_style = f"font-size: 12px; color: {COLORS['text_light']};"
        
        # 统计信息
        self.footer_stats_label = QLabel("检测: 0次")
        self.footer_stats_label.setStyleSheet(info_style)
        layout.addWidget(self.footer_stats_label)
        
        sep1 = QLabel("|")
        sep1.setStyleSheet(sep_style)
        layout.addWidget(sep1)
        
        self.footer_model_label = QLabel("模型: 未加载")
        self.footer_model_label.setStyleSheet(info_style)
        layout.addWidget(self.footer_model_label)
        
        sep2 = QLabel("|")
        sep2.setStyleSheet(sep_style)
        layout.addWidget(sep2)
        
        self.footer_time_label = QLabel("耗时: --")
        self.footer_time_label.setStyleSheet(info_style)
        layout.addWidget(self.footer_time_label)
        
        parent_layout.addWidget(footer)

    def _create_separator(self):
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {COLORS['border']}; margin: 6px 0;")
        return sep

    # ========== 样式方法 ==========
    def _style_button(self, btn, variant='primary'):
        colors = {
            'primary': (GRADIENTS['primary'], COLORS['primary_light'], COLORS['secondary_light']),
            'success': (GRADIENTS['success'], COLORS['success_light'], '#58d68d'),
            'danger': (GRADIENTS['danger'], COLORS['danger_light'], '#d35400'),
        }
        bg, h1, h2 = colors.get(variant, colors['primary'])
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ background: {bg}; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 12px; }}
            QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {h1}, stop:1 {h2}); }}
            QPushButton:disabled {{ background: #bdc3c7; }}
        """)

    def _style_small_button(self, btn, variant='primary'):
        colors = {'primary': COLORS['primary'], 'success': COLORS['success'], 'danger': COLORS['danger']}
        color = colors.get(variant, COLORS['primary'])
        btn.setCursor(Qt.PointingHandCursor)
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: rgba({r}, {g}, {b}, 0.1); 
                color: {color}; 
                border: 2px solid {color}; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 13px; 
            }}
            QPushButton:hover {{ 
                background: {color}; 
                color: white; 
            }}
        """)

    def _style_combo(self, combo):
        combo.setStyleSheet(f"""
            QComboBox {{ padding: 6px 10px; border: 1px solid {COLORS['border']}; border-radius: 6px; background: {COLORS['bg_white']}; font-size: 12px; }}
            QComboBox:hover {{ border-color: {COLORS['primary']}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid {COLORS['primary']}; }}
        """)

    def _style_slider(self, slider):
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 5px; background: {COLORS['bg_light']}; border-radius: 2px; }}
            QSlider::sub-page:horizontal {{ background: {GRADIENTS['primary']}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {COLORS['primary']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; border: 2px solid white; }}
        """)

    # ========== 事件处理 ==========
    def update_conf_threshold(self):
        value = self.conf_slider.value() / 100
        self.conf_value_label.setText(f"{value:.2f}")

    def on_detect_type_changed(self):
        if "图片" in self.detect_type_combo.currentText():
            self.detect_button.show()
            self.cam_buttons_widget.hide()
        else:
            self.detect_button.hide()
            self.cam_buttons_widget.show()
        self._reset_display()

    def _reset_display(self):
        self.result_label.clear()
        self.result_label.setText("点击「开始检测」选择图片")
        self.info_text.clear()
        self.image_info_label.setText("")
        self.current_results = None
        self.current_image_path = None
        self._update_stats(0, 0, 0)

    def _update_stats(self, count, avg_conf, time_ms):
        self.target_count_label.findChild(QLabel, "value").setText(str(count))
        self.avg_conf_label.findChild(QLabel, "value").setText(f"{avg_conf:.2f}" if avg_conf > 0 else "--")
        self.time_label.findChild(QLabel, "value").setText(f"{time_ms:.0f}" if time_ms > 0 else "--")

    def load_model_dialog(self):
        model_path, _ = QFileDialog.getOpenFileName(self, "选择YOLO模型", "", "模型文件 (*.pt)")
        if model_path:
            self._set_status("正在加载模型...", "loading")
            try:
                self.model = YOLO(model_path)
                self.model.to('cpu')
                model_name = os.path.basename(model_path)
                self.model_button.setText(model_name[:10] + "..." if len(model_name) > 10 else model_name)
                self.footer_model_label.setText(f"模型: {model_name[:12]}")
                self.detect_button.setEnabled(True)
                self._set_status("模型加载成功", "success")
            except Exception as e:
                self._set_status("模型加载失败", "error")
                QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")

    def _set_status(self, message, status_type="info"):
        colors = {
            "info": (COLORS['text_dark'], COLORS['success']),
            "success": (COLORS['success'], COLORS['success']),
            "error": (COLORS['danger'], COLORS['danger']),
            "loading": (COLORS['primary'], COLORS['warning'])
        }
        text_color, dot_color = colors.get(status_type, colors['info'])
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {text_color};")
        self.status_dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        if status_type in ["success", "error"]:
            QTimer.singleShot(3000, lambda: self._set_status("系统就绪", "info"))

    def start_detection(self):
        if not self.model:
            QMessageBox.warning(self, "警告", "请先加载模型!")
            return
        self._reset_display()
        if "图片" in self.detect_type_combo.currentText():
            self.detect_image()
        else:
            self.start_webcam()

    def detect_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)")
        if image_path:
            self.current_image_path = image_path
            self.detection_start_time = datetime.now()
            self.image_info_label.setText(os.path.basename(image_path))
            self._set_status("正在检测...", "loading")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.worker = DetectionWorker(self.model, "image", image_path, self.conf_slider.value() / 100)
            self.worker.detection_complete.connect(self.handle_detection_results)
            self.worker.error_occurred.connect(self.handle_error)
            self.detect_button.setEnabled(False)
            self.worker.start()

    def handle_detection_results(self, results):
        self.current_results = results
        self.detect_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        processing_time = 0.0
        if self.detection_start_time:
            processing_time = (datetime.now() - self.detection_start_time).total_seconds()
        
        if not results or len(results) == 0:
            self.result_label.setText("检测结果为空")
            self._set_status("检测完成，无结果", "info")
            return
        
        result = results[0]
        target_count = len(result.boxes) if hasattr(result, 'boxes') else 0
        
        if target_count == 0:
            self.result_label.setText("未检测到目标")
            self._set_status("检测完成，未发现目标", "info")
            return
        
        # 显示检测结果图像
        annotated = result.plot(line_width=2, font_size=12)
        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        h, w, ch = annotated.shape
        qImg = QImage(annotated.data, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        scaled = pixmap.scaled(self.result_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.result_label.setPixmap(scaled)
        
        # 计算统计
        all_confs = [float(box.conf[0].cpu().numpy()) for box in result.boxes]
        avg_conf = sum(all_confs) / len(all_confs) if all_confs else 0
        
        self._update_stats(target_count, avg_conf, processing_time * 1000)
        self.detection_count += 1
        self.footer_stats_label.setText(f"检测: {self.detection_count}次")
        self.footer_time_label.setText(f"耗时: {processing_time*1000:.0f}ms")
        self.update_detection_info(results, processing_time)
        
        if self.auto_save_check.isChecked():
            self._auto_save_to_history(results, processing_time, pixmap)
        
        self._set_status(f"检测完成，发现 {target_count} 个目标", "success")

    def _auto_save_to_history(self, results, processing_time, result_pixmap):
        try:
            from database.history_manager import history_manager
            if not self.current_image_path or not results:
                return
            result = results[0]
            detection_results = []
            confidence_scores = []
            for box in result.boxes:
                cls = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                class_name = result.names[cls] if hasattr(result, 'names') else f"class_{cls}"
                # 获取垃圾分类信息
                garbage_info = get_garbage_info(class_name)
                detection_results.append({
                    'class': class_name,
                    'name': garbage_info.get('名称', class_name),
                    'category': garbage_info.get('分类', '未知分类'),
                    'tips': garbage_info.get('处理建议', ''),
                    'confidence': conf
                })
                confidence_scores.append(conf)
            result_image_data = None
            if result_pixmap and not result_pixmap.isNull():
                from PyQt5.QtCore import QBuffer, QIODevice
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                result_pixmap.save(buffer, "JPG", 85)
                result_image_data = bytes(buffer.data())
                buffer.close()
            history_manager.save_detection_record(
                image_path=self.current_image_path,
                detection_results=detection_results,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                source_type='upload',
                result_image_data=result_image_data
            )
        except Exception as e:
            print(f"自动保存失败: {e}")

    def handle_error(self, error_msg):
        self.detect_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._set_status("检测失败", "error")
        QMessageBox.critical(self, "错误", f"检测失败: {error_msg}")

    def update_detection_info(self, results, processing_time=0.0):
        if not results:
            return
        result = results[0]
        target_count = len(result.boxes) if hasattr(result, 'boxes') else 0
        info_lines = []
        if target_count == 0:
            info_lines.append("未检测到目标")
        else:
            for i, box in enumerate(result.boxes):
                cls = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                class_name = result.names[cls] if hasattr(result, 'names') else f"类别{cls}"
                info_lines.append(f"[{i+1}] {class_name} ({conf:.0%})")
                garbage_info = get_garbage_info(class_name)
                if garbage_info:
                    info_lines.append(f"    分类: {garbage_info.get('分类', '未知')}")
                    info_lines.append(f"    处理: {garbage_info.get('处理建议', '请咨询当地标准')}")
                info_lines.append("")
        self.info_text.setText("\n".join(info_lines))

    # ========== 摄像头相关 ==========
    def start_webcam(self):
        if not self.model:
            QMessageBox.warning(self, "警告", "请先加载模型!")
            return
        try:
            self._set_status("正在启动摄像头...", "loading")
            self.webcam_worker = WebcamWorker(self.model, self.conf_slider.value() / 100)
            self.webcam_worker.frame_ready.connect(self.display_webcam_frame)
            self.webcam_worker.result_ready.connect(self.display_webcam_result)
            self.webcam_worker.detection_complete.connect(lambda r: self.update_detection_info(r, 0))
            self.webcam_worker.start()
            self._set_status("摄像头已启动", "success")
        except Exception as e:
            self._set_status("摄像头启动失败", "error")
            QMessageBox.critical(self, "错误", str(e))

    def stop_webcam(self):
        if hasattr(self, 'webcam_worker') and self.webcam_worker and self.webcam_worker.isRunning():
            self.webcam_worker.stop()
            self.webcam_worker.wait()
            self._reset_display()
            self._set_status("摄像头已停止", "info")

    def display_webcam_frame(self, frame):
        pass

    def display_webcam_result(self, frame):
        h, w, ch = frame.shape
        qImg = QImage(frame.data, w, h, 3 * w, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qImg)
        scaled = pixmap.scaled(self.result_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.result_label.setPixmap(scaled)

    # ========== 辅助功能 ==========
    def go_to_history(self):
        if self.parent_window and hasattr(self.parent_window, 'stack') and hasattr(self.parent_window, 'page_history'):
            self.parent_window.stack.setCurrentWidget(self.parent_window.page_history)
            if hasattr(self.parent_window.page_history, 'load_history'):
                self.parent_window.page_history.load_history()

    def export_result(self):
        if not self.current_results:
            QMessageBox.information(self, "提示", "暂无检测结果可导出")
            return
        pixmap = self.result_label.pixmap()
        if pixmap and not pixmap.isNull():
            file_path, _ = QFileDialog.getSaveFileName(self, "保存检测结果", f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", "图片文件 (*.jpg *.png)")
            if file_path:
                pixmap.save(file_path)
                QMessageBox.information(self, "成功", f"已保存到: {file_path}")

    def get_conf_threshold(self):
        return self.conf_slider.value() / 100
