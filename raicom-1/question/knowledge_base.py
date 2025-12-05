"""
垃圾分类AI问答助手 - 简化版固定布局
"""
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTextEdit, QApplication, QFrame, QSizePolicy, QDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor
from ollama.ollama_client import OllamaClient
from window.styles import COLORS, GRADIENTS


COMMON_QUESTIONS = [
    "塑料瓶属于什么垃圾？",
    "电池应该怎么处理？",
    "剩饭剩菜是什么垃圾？",
    "玻璃瓶可以回收吗？",
    "过期药品怎么处理？",
    "什么是可回收垃圾？",
]


class ChatWorker(QThread):
    """聊天工作线程"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, client, question):
        super().__init__()
        self.client = client
        self.question = question
    
    def run(self):
        try:
            response = self.client.get_garbage_classification_answer(self.question)
            if response:
                self.response_received.emit(response)
            else:
                self.error_occurred.emit("获取回答失败")
        except Exception as e:
            self.error_occurred.emit(f"处理请求时出错: {str(e)}")
        finally:
            self.finished.emit()


class KnowledgeBaseWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("垃圾分类AI问答助手")
        self.setMinimumSize(900, 550)
        
        self.ollama_client = OllamaClient()
        self.chat_worker = None
        
        self.setup_ui()
        self.test_connection()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # 标题栏
        header_layout = QHBoxLayout()
        title = QLabel("垃圾分类AI问答助手")
        title.setStyleSheet(f"""
            font-size: 24px; 
            font-weight: bold; 
            color: {COLORS['text_dark']}; 
            font-family: 'Microsoft YaHei', Arial;
            letter-spacing: 2px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.status_label = QLabel("● 未连接")
        self.status_label.setStyleSheet(f"font-size: 14px; color: {COLORS['danger']}; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # 内容区：左侧常见问题 + 右侧聊天
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # 左侧：常见问题（固定宽度240px）
        left_widget = QWidget()
        left_widget.setFixedWidth(240)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        common_label = QLabel("常见问题")
        common_label.setFixedHeight(40)
        common_label.setAlignment(Qt.AlignCenter)
        common_label.setStyleSheet(f"""
            QLabel {{
                background: {GRADIENTS['primary']};
                color: {COLORS['text_white']};
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                letter-spacing: 2px;
            }}
        """)
        left_layout.addWidget(common_label)
        
        for question in COMMON_QUESTIONS:
            btn = QPushButton(question)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 14px;
                    background: {COLORS['bg_white']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    color: {COLORS['text_dark']};
                }}
                QPushButton:hover {{
                    background: rgba(102, 126, 234, 0.1);
                    border-color: {COLORS['primary']};
                    color: {COLORS['primary']};
                }}
            """)
            btn.clicked.connect(lambda checked, q=question: self.ask_question(q))
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        content_layout.addWidget(left_widget)

        # 右侧：聊天区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 聊天显示
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                line-height: 1.6;
                font-family: 'Microsoft YaHei', Arial;
            }}
        """)
        right_layout.addWidget(self.chat_display, 1)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("请输入您的问题...")
        self.input_edit.setFixedHeight(45)
        self.input_edit.returnPressed.connect(self.send_question)
        self.input_edit.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                font-size: 15px;
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                background: {COLORS['bg_white']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        input_layout.addWidget(self.input_edit, 1)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(90, 45)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_question)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GRADIENTS['primary']};
                color: {COLORS['text_white']};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
            }}
            QPushButton:disabled {{
                background: #bdc3c7;
            }}
        """)
        input_layout.addWidget(self.send_btn)
        
        right_layout.addLayout(input_layout)
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # 初始消息
        self.add_message("AI", "您好！我是垃圾分类AI助手，可以回答您关于垃圾分类的问题。")

    def test_connection(self):
        """测试连接"""
        if self.ollama_client.test_connection():
            self.status_label.setText("● 已连接")
            self.status_label.setStyleSheet(f"font-size: 14px; color: {COLORS['success']}; font-weight: bold;")
        else:
            self.status_label.setText("● 未连接")
            self.status_label.setStyleSheet(f"font-size: 14px; color: {COLORS['danger']}; font-weight: bold;")
    
    def add_message(self, sender, message):
        """添加消息"""
        current = self.chat_display.toHtml()
        if sender == "AI":
            new_msg = f"""
            <div style="margin: 10px 0; padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <strong>AI助手</strong>: {message}
            </div>
            """
        else:
            new_msg = f"""
            <div style="margin: 10px 0; padding: 12px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196f3;">
                <strong>我</strong>: {message}
            </div>
            """
        self.chat_display.setHtml(current + new_msg)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
    
    def ask_question(self, question):
        """询问问题"""
        if not question.strip():
            return
        self.add_message("我", question)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("处理中...")
        
        self.chat_worker = ChatWorker(self.ollama_client, question)
        self.chat_worker.response_received.connect(self.handle_response)
        self.chat_worker.error_occurred.connect(self.handle_error)
        self.chat_worker.finished.connect(self.handle_finished)
        self.chat_worker.start()
    
    def send_question(self):
        """发送问题"""
        question = self.input_edit.text().strip()
        if question:
            self.input_edit.clear()
            self.ask_question(question)
    
    def handle_response(self, response):
        self.add_message("AI", response)
    
    def handle_error(self, error_msg):
        self.add_message("AI", f"抱歉，出现错误：{error_msg}")
    
    def handle_finished(self):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = KnowledgeBaseWindow()
    win.show()
    sys.exit(app.exec_())
