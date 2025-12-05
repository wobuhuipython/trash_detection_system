"""
历史记录查看界面 - 简化版固定布局
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QScrollArea, QComboBox, QSpinBox,
    QProgressBar, QTextEdit, QFileDialog, QCheckBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor
from database.history_manager import history_manager, HistoryWorker
import os
from datetime import datetime
from window.styles import COLORS, GRADIENTS


class HistoryWindow(QWidget):
    """历史记录查看窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("检测历史记录")
        self.setMinimumSize(600, 400)
        
        self.current_history = []
        self.current_page = 0
        self.page_size = 20
        self.total_records = 0
        self.last_update_time = None
        self.auto_refresh_enabled = False
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_for_updates)
        self.history_worker = None
        
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # 标题栏
        self._create_header(main_layout)
        
        # 控制面板
        self._create_control_panel(main_layout)
        
        # 内容区：左侧表格 + 右侧详情（固定比例）
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧：表格区域（占60%）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        self._create_table(left_layout)
        self._create_pagination(left_layout)
        content_layout.addWidget(left_widget, 6)
        
        # 右侧：详情区域（占40%）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        self._create_detail_panel(right_layout)
        content_layout.addWidget(right_widget, 4)
        
        main_layout.addLayout(content_layout, 1)
        
        # 状态栏
        self._create_status_bar(main_layout)
        
        self._apply_styles()
    
    def _add_shadow(self, widget, blur=20, offset=4, color=QColor(102, 126, 234, 45)):
        """为控件添加阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    def _create_header(self, parent_layout):
        """创建标题栏"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        
        title = QLabel("检测历史记录")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_dark']};
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("查看和管理您的检测记录")
        subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_light']};
            margin-left: 15px;
        """)
        layout.addWidget(subtitle)
        layout.addStretch()
        
        parent_layout.addLayout(layout)
    
    def _create_control_panel(self, parent_layout):
        """创建控制面板"""
        panel = QFrame()
        panel.setFixedHeight(50)
        panel.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)
        
        # 筛选
        layout.addWidget(QLabel("筛选:"))
        self.source_filter = QComboBox()
        self.source_filter.addItems(["全部", "图片上传", "摄像头检测"])
        self.source_filter.setFixedWidth(120)
        self.source_filter.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.source_filter)
        
        # 每页
        layout.addWidget(QLabel("每页:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 100)
        self.page_size_spin.setValue(20)
        self.page_size_spin.setFixedWidth(70)
        self.page_size_spin.valueChanged.connect(self.on_page_size_changed)
        layout.addWidget(self.page_size_spin)
        
        layout.addStretch()
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedSize(80, 35)
        self.refresh_btn.clicked.connect(self.manual_refresh)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self._style_button(self.refresh_btn, 'primary')
        layout.addWidget(self.refresh_btn)
        
        # 清理按钮
        self.clear_btn = QPushButton("清理旧记录")
        self.clear_btn.setFixedSize(100, 35)
        self.clear_btn.clicked.connect(self.clear_old_records)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self._style_button(self.clear_btn, 'danger')
        layout.addWidget(self.clear_btn)
        
        parent_layout.addWidget(panel)
    
    def _create_table(self, parent_layout):
        """创建表格"""
        # 表格标题
        title = QLabel("检测记录列表")
        title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_dark']};
            padding: 5px 0;
        """)
        parent_layout.addWidget(title)
        
        # 表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["ID", "检测时间", "来源", "检测结果", "置信度"])
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setColumnWidth(0, 50)
        self.history_table.setColumnWidth(1, 150)
        self.history_table.setColumnWidth(2, 100)
        self.history_table.setColumnWidth(3, 180)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setShowGrid(False)
        self.history_table.selectionModel().selectionChanged.connect(self.on_record_selected)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        parent_layout.addWidget(self.history_table, 1)
    
    def _create_pagination(self, parent_layout):
        """创建分页"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setFixedSize(80, 32)
        self.prev_btn.clicked.connect(self.prev_page)
        self._style_button(self.prev_btn, 'primary')
        layout.addWidget(self.prev_btn)
        
        self.page_info_label = QLabel("第 1 页")
        self.page_info_label.setAlignment(Qt.AlignCenter)
        self.page_info_label.setFixedWidth(100)
        layout.addWidget(self.page_info_label)
        
        self.next_btn = QPushButton("下一页")
        self.next_btn.setFixedSize(80, 32)
        self.next_btn.clicked.connect(self.next_page)
        self._style_button(self.next_btn, 'primary')
        layout.addWidget(self.next_btn)
        
        layout.addStretch()
        
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.setFixedSize(90, 32)
        self.delete_btn.clicked.connect(self.delete_selected_record)
        self.delete_btn.setEnabled(False)
        self._style_button(self.delete_btn, 'danger')
        layout.addWidget(self.delete_btn)
        
        parent_layout.addLayout(layout)
    
    def _create_detail_panel(self, parent_layout):
        """创建详情面板"""
        # 标题
        title = QLabel("记录详情")
        title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_dark']};
            padding: 5px 0;
        """)
        parent_layout.addWidget(title)
        
        # 详情卡片
        detail_card = QFrame()
        detail_card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        
        card_layout = QVBoxLayout(detail_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        
        # 图片显示
        self.image_label = QLabel("选择左侧记录查看")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(180)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['bg_light']};
                border: 2px dashed {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_light']};
                font-size: 14px;
            }}
        """)
        card_layout.addWidget(self.image_label, 1)
        
        # 详情文本
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(130)
        self.detail_text.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: {COLORS['text_dark']};
            }}
        """)
        card_layout.addWidget(self.detail_text)
        
        # 导出按钮
        self.export_btn = QPushButton("导出图片")
        self.export_btn.setFixedHeight(36)
        self.export_btn.clicked.connect(self.export_image)
        self.export_btn.setEnabled(False)
        self._style_button(self.export_btn, 'primary')
        card_layout.addWidget(self.export_btn)
        
        parent_layout.addWidget(detail_card, 1)
    
    def _create_status_bar(self, parent_layout):
        """创建状态栏"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 0)
        layout.setSpacing(15)
        
        # 状态点
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")
        layout.addWidget(status_dot)
        
        self.stats_label = QLabel("总记录数: 0")
        self.stats_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_dark']}; font-size: 13px;")
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(120, 8)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background: #e0e0e0;
            }}
            QProgressBar::chunk {{
                background: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        parent_layout.addLayout(layout)
    
    def _style_button(self, btn, variant='primary'):
        """设置按钮样式"""
        colors = {
            'primary': (GRADIENTS['primary'], COLORS['primary_light'], COLORS['secondary_light']),
            'success': (GRADIENTS['success'], COLORS['success_light'], '#58d68d'),
            'danger': (GRADIENTS['danger'], COLORS['danger_light'], '#d35400'),
        }
        bg, hover1, hover2 = colors.get(variant, colors['primary'])
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {COLORS['text_white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {hover1}, stop:1 {hover2});
            }}
            QPushButton:disabled {{
                background: #bdc3c7;
            }}
        """)
    
    def _apply_styles(self):
        """应用全局样式"""
        self.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_light']};
                font-family: 'Microsoft YaHei', 'Segoe UI', Arial;
            }}
            QTableWidget {{
                background: white;
                alternate-background-color: #f8f9fa;
                gridline-color: {COLORS['border']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableWidget::item:selected {{
                background: rgba(102, 126, 234, 0.15);
                color: {COLORS['primary']};
            }}
            QTableWidget::item:hover {{
                background: rgba(102, 126, 234, 0.08);
            }}
            QHeaderView::section {{
                background: #f5f7fa;
                padding: 10px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: bold;
                font-size: 13px;
                color: {COLORS['text_dark']};
            }}
            QComboBox, QSpinBox {{
                padding: 8px 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: white;
                font-size: 13px;
            }}
            QComboBox:hover, QSpinBox:hover {{
                border-color: {COLORS['primary']};
            }}
        """)

    # ========== 数据操作方法 ==========
    
    def load_history(self):
        """加载历史记录"""
        self.show_progress()
        source_filter = self.source_filter.currentText()
        source_type = None
        if source_filter == "图片上传":
            source_type = "upload"
        elif source_filter == "摄像头检测":
            source_type = "camera"
        
        self.history_worker = HistoryWorker(
            'load_history',
            limit=self.page_size,
            offset=self.current_page * self.page_size,
            source_type=source_type
        )
        self.history_worker.history_loaded.connect(self.on_history_loaded)
        self.history_worker.start()
    
    def on_history_loaded(self, history):
        """历史记录加载完成"""
        self.current_history = history
        self.update_table()
        self.update_pagination()
        self.update_stats()
        self.hide_progress()
        if history:
            self.last_update_time = history[0]['detection_time']
    
    def update_table(self):
        """更新表格"""
        self.history_table.setRowCount(len(self.current_history))
        for row, record in enumerate(self.current_history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
            time_str = record['detection_time'].strftime('%Y-%m-%d %H:%M:%S')
            self.history_table.setItem(row, 1, QTableWidgetItem(time_str))
            source_text = "图片上传" if record['source_type'] == 'upload' else "摄像头"
            self.history_table.setItem(row, 2, QTableWidgetItem(source_text))
            
            results = record['detection_results']
            if results:
                if len(results) == 1:
                    result_text = f"{results[0].get('class', '未知')}"
                else:
                    result_text = f"{len(results)}个目标"
            else:
                result_text = "无结果"
            self.history_table.setItem(row, 3, QTableWidgetItem(result_text))
            
            confidences = record['confidence_scores']
            conf_text = f"{sum(confidences)/len(confidences):.2f}" if confidences else "N/A"
            self.history_table.setItem(row, 4, QTableWidgetItem(conf_text))
    
    def update_pagination(self):
        """更新分页"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.page_info_label.setText(f"第 {self.current_page + 1}/{total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page + 1 < total_pages)
    
    def update_stats(self):
        """更新统计"""
        source_filter = self.source_filter.currentText()
        source_type = None
        if source_filter == "图片上传":
            source_type = "upload"
        elif source_filter == "摄像头检测":
            source_type = "camera"
        self.total_records = history_manager.get_detection_count(source_type)
        self.stats_label.setText(f"总记录数: {self.total_records}")
    
    def on_record_selected(self):
        """记录选择"""
        row = self.history_table.currentRow()
        if 0 <= row < len(self.current_history):
            self.show_record_detail(self.current_history[row])
            self.delete_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
        else:
            self.delete_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
    
    def show_record_detail(self, record):
        """显示详情"""
        # 优先显示检测结果图片
        image_data = history_manager.get_result_image_data(record['id'])
        if not image_data:
            image_data = history_manager.get_image_data(record['id'])
        
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("图片不可用")
        
        # 构建详细信息
        detail_lines = []
        detail_lines.append(f"【记录ID】{record['id']}")
        detail_lines.append(f"【检测时间】{record['detection_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        detail_lines.append(f"【来源】{'图片上传' if record['source_type'] == 'upload' else '摄像头检测'}")
        detail_lines.append(f"【处理耗时】{record['processing_time']:.2f}秒")
        detail_lines.append("-" * 30)
        
        results = record['detection_results']
        if results:
            detail_lines.append(f"【检测目标】共 {len(results)} 个")
            for i, r in enumerate(results[:5]):  # 最多显示5个
                detail_lines.append(f"  {i+1}. {r.get('class', '未知')} ({r.get('confidence', 0):.2f})")
            if len(results) > 5:
                detail_lines.append(f"  ... 还有 {len(results)-5} 个目标")
        else:
            detail_lines.append("【检测目标】无")
        
        self.detail_text.setText("\n".join(detail_lines))
    
    # ========== 事件处理 ==========
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_history()
    
    def next_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page + 1 < total_pages:
            self.current_page += 1
            self.load_history()
    
    def on_filter_changed(self):
        self.current_page = 0
        self.load_history()
    
    def on_page_size_changed(self):
        self.page_size = self.page_size_spin.value()
        self.current_page = 0
        self.load_history()
    
    def manual_refresh(self):
        self.load_history()
    
    def delete_selected_record(self):
        row = self.history_table.currentRow()
        if 0 <= row < len(self.current_history):
            record = self.current_history[row]
            reply = QMessageBox.question(self, "确认删除", f"确定删除记录 {record['id']}？")
            if reply == QMessageBox.Yes:
                self.history_worker = HistoryWorker('delete_record', record_id=record['id'])
                self.history_worker.operation_completed.connect(self.on_delete_completed)
                self.history_worker.start()
    
    def on_delete_completed(self, success, message):
        self.hide_progress()
        if success:
            QMessageBox.information(self, "成功", message)
            self.load_history()
        else:
            QMessageBox.warning(self, "失败", message)
    
    def export_image(self):
        row = self.history_table.currentRow()
        if 0 <= row < len(self.current_history):
            record = self.current_history[row]
            filename = f"detection_{record['id']}.jpg"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出图片", filename, "图片 (*.jpg *.png)")
            if file_path:
                # 优先导出检测结果图片
                image_data = history_manager.get_result_image_data(record['id'])
                if not image_data:
                    image_data = history_manager.get_image_data(record['id'])
                
                if image_data:
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    QMessageBox.information(self, "成功", f"已保存到: {file_path}")
                else:
                    QMessageBox.warning(self, "失败", "图片数据不可用")
    
    def clear_old_records(self):
        reply = QMessageBox.question(self, "确认清理", "清理30天前的记录？")
        if reply == QMessageBox.Yes:
            self.history_worker = HistoryWorker('clear_old', days=30)
            self.history_worker.operation_completed.connect(self.on_clear_completed)
            self.history_worker.start()
    
    def on_clear_completed(self, success, message):
        self.hide_progress()
        if success:
            QMessageBox.information(self, "成功", message)
            self.load_history()
    
    def check_for_updates(self):
        pass  # 简化版不实现自动刷新
    
    def toggle_auto_refresh(self, state):
        pass
    
    def update_refresh_interval(self, value):
        pass
    
    def show_progress(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
    
    def hide_progress(self):
        self.progress_bar.setVisible(False)
    
    def clear_status_notification(self):
        pass
