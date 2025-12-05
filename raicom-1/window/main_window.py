import os
import webbrowser
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget,
                             QPushButton, QHBoxLayout, QStackedWidget, 
                             QGraphicsDropShadowEffect, QFrame, QMessageBox)
from PyQt5.QtGui import QPixmap, QColor, QDesktopServices
from detection.detection_page import DetectionPage
from question.knowledge_base import KnowledgeBaseWindow
from window.history_window import HistoryWindow
from window.styles import COLORS, GRADIENTS

# 官网地址配置
WEBSITE_URL = "http://localhost:5173"  # Vue3开发服务器默认地址，部署后改为实际地址

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("生活垃圾分类应用")
        # 设置窗口大小
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 侧边栏 - 固定宽度220px
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        # 设置侧边栏渐变背景 - 更现代的深色风格
        self.sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1f36, stop:0.3 #161b2e, stop:0.7 #121726, stop:1 #0d111e);
                border-right: 1px solid rgba(102, 126, 234, 0.2);
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 15)
        sidebar_layout.setSpacing(12)


        # 侧边栏按钮
        self.btn_home = QPushButton("首页")
        self.btn_detect = QPushButton("识别检测")
        self.btn_knowledge = QPushButton("问答助手")
        self.btn_history = QPushButton("检测历史")
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_detect)
        sidebar_layout.addWidget(self.btn_knowledge)
        sidebar_layout.addWidget(self.btn_history)
        
        sidebar_layout.addStretch()
        
        # 分隔线
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(102, 126, 234, 0.3); margin: 10px 5px;")
        sidebar_layout.addWidget(separator)
        
        # 官网入口按钮 - 特殊样式
        self.btn_website = QPushButton("🌐 科普官网")
        self.btn_website.setFixedHeight(48)
        self.btn_website.setCursor(Qt.PointingHandCursor)
        self.btn_website.setToolTip("打开垃圾分类科普知识平台")
        self.btn_website.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                font-size: 14px;
                border-radius: 12px;
                padding: 10px 18px;
                margin: 4px 0;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.2);
                text-align: center;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2ecc71, stop:1 #58d68d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #27ae60);
            }
        """)
        self.btn_website.clicked.connect(self.open_website)
        sidebar_layout.addWidget(self.btn_website)

        # 设置按钮样式
        for btn in [self.btn_home, self.btn_detect, self.btn_knowledge, self.btn_history]:
            self.add_button_style(btn)

        # 主内容区
        self.stack = QStackedWidget()
        self.page_home = self.create_home_page()
        self.page_detect = DetectionPage(self)
        self.page_knowledge = KnowledgeBaseWindow(self)
        self.page_history = HistoryWindow(self)
        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_detect)
        self.stack.addWidget(self.page_knowledge)
        self.stack.addWidget(self.page_history)

        # 固定布局：侧边栏固定宽度，内容区自适应
        self.sidebar.setFixedWidth(220)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)  # 内容区占据剩余空间

        # 按钮切换
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_home))
        self.btn_detect.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_detect))
        self.btn_knowledge.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_knowledge))
        self.btn_history.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_history))

        # 初始化 settings 属性
        self.settings = {
            'output_directory': os.path.expanduser("~")
        }

    def create_home_page(self):
        page = QWidget()
        # 设置背景图 - 自适应填充
        self.bg_pixmap = QPixmap(r"E:\毕设项目代码\raicom-1\images\shouye.jpg")
        self.bg_label = QLabel(page)
        self.bg_label.setScaledContents(True)  # 允许内容缩放
        self.bg_label.setGeometry(page.rect())
        self.bg_label.lower()
        
        # 初始设置背景图片 - 使用page而不是self.page_home
        self._update_background_initial(page)

        # 使用垂直布局，让文字覆盖在背景图片上
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建文字容器，使用绝对定位覆盖在背景上
        self.text_container = QWidget(page)
        self.text_container.setAttribute(Qt.WA_TransparentForMouseEvents)  # 允许鼠标事件穿透
        self.text_container.setStyleSheet("background: transparent;")
        
        # 文字布局
        text_layout = QVBoxLayout(self.text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        # 欢迎文字 - 使用绝对定位，根据背景图片内容区域定位
        self.home_welcome = QLabel("欢迎使用校园垃圾分类应用")
        self.home_welcome.setAlignment(Qt.AlignCenter)
        self.home_welcome.setWordWrap(False)
        self.home_welcome.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.92), stop:0.5 rgba(118, 75, 162, 0.92), stop:1 rgba(107, 141, 214, 0.92));
                border-radius: 20px;
                padding: 28px 55px;
                margin: 15px;
                min-width: 600px;
                max-width: 900px;
                text-align: center;
                border: 2px solid rgba(255, 255, 255, 0.25);
                letter-spacing: 3px;
                font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            }
        """)
        # 添加柔和的阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(102, 126, 234, 150))
        shadow.setOffset(0, 8)
        self.home_welcome.setGraphicsEffect(shadow)
        
        # 将欢迎文字放在图片正上方（顶部区域）
        text_layout.addWidget(self.home_welcome, 0, Qt.AlignCenter)  # 顶部居中对齐
        text_layout.addStretch(1)  # 下方弹性空间

        # 添加弹性空间到主布局
        main_layout.addStretch(1)

        # 初始化文字容器位置
        self.text_container.setGeometry(page.rect())
        
        # 让page支持resizeEvent
        page.resizeEvent = self._home_resize_event
        return page

    def _home_resize_event(self, event):
        # 只影响首页背景
        if hasattr(self, 'bg_label') and hasattr(self, 'bg_pixmap'):
            self.bg_label.setGeometry(self.page_home.rect())
            self._update_background()
        
        # 更新文字容器尺寸，使其填满整个页面
        if hasattr(self, 'text_container'):
            self.text_container.setGeometry(self.page_home.rect())
        
        # 首页尺寸变化时，同步更新文字样式
        self._apply_home_styles()
        QWidget.resizeEvent(self.page_home, event)

    def resizeEvent(self, event):
        # 只在首页时调整背景
        if self.stack.currentWidget() == self.page_home:
            if hasattr(self, 'bg_label') and hasattr(self, 'bg_pixmap'):
                self.bg_label.setGeometry(self.page_home.rect())
                self._update_background()
            if hasattr(self, 'text_container'):
                self.text_container.setGeometry(self.page_home.rect())
        super().resizeEvent(event)

    def _update_background_initial(self, page):
        """初始化背景图片"""
        if not hasattr(self, 'bg_pixmap') or not hasattr(self, 'bg_label'):
            return
            
        # 获取当前页面尺寸
        page_size = page.size()
        
        # 使用IgnoreAspectRatio填满整个页面，避免留白导致分割线不对齐
        final_pixmap = self.bg_pixmap.scaled(
            page_size.width(), page_size.height(),
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 设置背景图片
        self.bg_label.setPixmap(final_pixmap)
        
        # 填满显示
        self.bg_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # 强制刷新显示
        self.bg_label.update()

    def _update_background(self):
        """更新背景图片，支持多种自适应模式"""
        if not hasattr(self, 'bg_pixmap') or not hasattr(self, 'bg_label'):
            return
            
        # 获取当前页面尺寸
        page_size = self.page_home.size()
        
        # 使用IgnoreAspectRatio填满整个页面，避免留白导致分割线不对齐
        final_pixmap = self.bg_pixmap.scaled(
            page_size.width(), page_size.height(),
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 设置背景图片
        self.bg_label.setPixmap(final_pixmap)
        
        # 填满显示
        self.bg_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # 强制刷新显示
        self.bg_label.update()

    def add_button_style(self, btn):
        """设置侧边栏按钮样式"""
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.9), stop:1 rgba(118, 75, 162, 0.9));
                color: white;
                font-size: 14px;
                border-radius: 12px;
                padding: 10px 18px;
                margin: 4px 0;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                letter-spacing: 2px;
                font-family: 'Microsoft YaHei', Arial;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['secondary_dark']});
            }}
        """)

    def _apply_home_styles(self):
        """更新首页欢迎文字样式"""
        if hasattr(self, 'home_welcome') and self.home_welcome:
            self.home_welcome.setStyleSheet(f"""
                QLabel {{
                    font-size: 28px;
                    font-weight: bold;
                    color: {COLORS['text_white']};
                    background: {GRADIENTS['primary']};
                    border-radius: 20px;
                    padding: 30px 50px;
                    margin: 20px;
                    text-align: center;
                    border: 2px solid rgba(255, 255, 255, 0.25);
                    letter-spacing: 3px;
                    font-family: 'Microsoft YaHei', Arial;
                }}
            """)

    def open_website(self):
        """打开垃圾分类科普官网"""
        try:
            # 使用系统默认浏览器打开
            QDesktopServices.openUrl(QUrl(WEBSITE_URL))
        except Exception as e:
            # 备用方案：使用webbrowser模块
            try:
                webbrowser.open(WEBSITE_URL)
            except Exception as e2:
                QMessageBox.warning(
                    self, 
                    "无法打开网页", 
                    f"无法打开官网，请手动访问：\n{WEBSITE_URL}\n\n错误信息：{str(e2)}"
                )

