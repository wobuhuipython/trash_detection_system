"""
统一样式配置文件 - 现代化UI设计
提供一致的颜色方案、渐变、阴影和动画效果
"""

# 主色调配置
COLORS = {
    'primary': '#667eea',           # 主色 - 紫蓝色
    'primary_light': '#7c8ef5',     # 主色浅
    'primary_dark': '#5a6fd6',      # 主色深
    'secondary': '#764ba2',         # 次色 - 紫色
    'secondary_light': '#8b5fbf',   # 次色浅
    'secondary_dark': '#6a4192',    # 次色深
    'success': '#27ae60',           # 成功 - 绿色
    'success_light': '#2ecc71',
    'warning': '#f39c12',           # 警告 - 橙色
    'warning_light': '#f1c40f',
    'danger': '#e74c3c',            # 危险 - 红色
    'danger_light': '#ec7063',
    'info': '#3498db',              # 信息 - 蓝色
    'info_light': '#5dade2',
    'text_dark': '#2c3e50',         # 深色文字
    'text_light': '#7f8c8d',        # 浅色文字
    'text_white': '#ffffff',        # 白色文字
    'bg_light': '#f8f9fa',          # 浅色背景
    'bg_white': '#ffffff',          # 白色背景
    'border': '#e1e8ed',            # 边框色
    'border_light': '#dee2e6',      # 浅边框
    'shadow': 'rgba(0, 0, 0, 0.1)', # 阴影色
}

# 渐变配置
GRADIENTS = {
    'primary': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2)',
    'primary_vertical': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #667eea, stop:1 #764ba2)',
    'primary_diagonal': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:0.5 #764ba2, stop:1 #6B8DD6)',
    'success': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71)',
    'danger': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b)',
    'warning': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f39c12, stop:1 #e67e22)',
    'sidebar': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460)',
    'card': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f8f9fa)',
    'glass': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,0.95), stop:1 rgba(248,249,250,0.9))',
}


def get_button_style(scale_func=None, variant='primary'):
    """获取按钮样式
    
    Args:
        scale_func: 缩放函数，用于响应式设计
        variant: 按钮变体 - primary/success/danger/warning/outline
    """
    s = scale_func if scale_func else lambda x: x
    
    variants = {
        'primary': {
            'bg': GRADIENTS['primary'],
            'bg_hover': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']})",
            'bg_pressed': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['secondary_dark']})",
        },
        'success': {
            'bg': GRADIENTS['success'],
            'bg_hover': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['success_light']}, stop:1 #58d68d)",
            'bg_pressed': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e8449, stop:1 {COLORS['success']})",
        },
        'danger': {
            'bg': GRADIENTS['danger'],
            'bg_hover': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['danger_light']}, stop:1 #d35400)",
            'bg_pressed': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #a93226)",
        },
        'warning': {
            'bg': GRADIENTS['warning'],
            'bg_hover': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['warning_light']}, stop:1 #f5b041)",
            'bg_pressed': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d68910, stop:1 #b9770e)",
        },
    }
    
    v = variants.get(variant, variants['primary'])
    
    return f"""
        QPushButton {{
            background: {v['bg']};
            color: {COLORS['text_white']};
            font-size: {s(16)}px;
            font-weight: 600;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            border: none;
            border-radius: {s(12)}px;
            padding: {s(14)}px {s(24)}px;
            min-height: {s(48)}px;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background: {v['bg_hover']};
        }}
        QPushButton:pressed {{
            background: {v['bg_pressed']};
        }}
        QPushButton:disabled {{
            background: #bdc3c7;
            color: #95a5a6;
        }}
    """


def get_sidebar_button_style(scale_func=None):
    """获取侧边栏按钮样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QPushButton {{
            background: {GRADIENTS['primary_diagonal']};
            color: {COLORS['text_white']};
            font-size: {s(18)}px;
            font-weight: 600;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            border: none;
            border-radius: {s(14)}px;
            padding: {s(16)}px {s(24)}px;
            margin: {s(8)}px 0;
            text-align: center;
            letter-spacing: 2px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 {COLORS['primary_light']}, stop:0.5 {COLORS['secondary_light']}, stop:1 #7fa0e8);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 {COLORS['primary_dark']}, stop:0.5 {COLORS['secondary_dark']}, stop:1 #5f7dc0);
        }}
    """


def get_card_style(scale_func=None):
    """获取卡片样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QFrame {{
            background: {COLORS['bg_white']};
            border: {s(1)}px solid {COLORS['border']};
            border-radius: {s(16)}px;
            padding: {s(20)}px;
        }}
    """


def get_title_label_style(scale_func=None, size='medium'):
    """获取标题标签样式"""
    s = scale_func if scale_func else lambda x: x
    
    sizes = {
        'small': s(18),
        'medium': s(22),
        'large': s(28),
        'xlarge': s(36),
    }
    font_size = sizes.get(size, sizes['medium'])
    
    return f"""
        QLabel {{
            font-size: {font_size}px;
            font-weight: bold;
            color: {COLORS['text_white']};
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            background: {GRADIENTS['primary']};
            padding: {s(14)}px {s(20)}px;
            border-radius: {s(12)}px;
            letter-spacing: 2px;
        }}
    """


def get_input_style(scale_func=None):
    """获取输入框样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QLineEdit, QTextEdit {{
            background-color: {COLORS['bg_white']};
            border: {s(2)}px solid {COLORS['border']};
            border-radius: {s(10)}px;
            padding: {s(12)}px {s(16)}px;
            font-size: {s(15)}px;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            color: {COLORS['text_dark']};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_white']};
        }}
        QLineEdit:hover, QTextEdit:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """


def get_combobox_style(scale_func=None):
    """获取下拉框样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QComboBox {{
            background-color: {COLORS['bg_white']};
            border: {s(2)}px solid {COLORS['border']};
            border-radius: {s(10)}px;
            padding: {s(10)}px {s(16)}px;
            font-size: {s(15)}px;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            min-height: {s(28)}px;
            color: {COLORS['text_dark']};
        }}
        QComboBox:hover {{
            border-color: {COLORS['primary']};
        }}
        QComboBox:focus {{
            border-color: {COLORS['primary']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: {s(32)}px;
            subcontrol-position: right center;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: {s(6)}px solid transparent;
            border-right: {s(6)}px solid transparent;
            border-top: {s(6)}px solid {COLORS['primary']};
            margin-right: {s(12)}px;
        }}
        QComboBox QAbstractItemView {{
            border: {s(2)}px solid {COLORS['border']};
            border-radius: {s(8)}px;
            background-color: {COLORS['bg_white']};
            selection-background-color: rgba(102, 126, 234, 0.15);
            selection-color: {COLORS['primary']};
            padding: {s(4)}px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: {s(8)}px {s(12)}px;
            min-height: {s(32)}px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: rgba(102, 126, 234, 0.1);
        }}
    """


def get_slider_style(scale_func=None):
    """获取滑块样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QSlider::groove:horizontal {{
            height: {s(8)}px;
            background: {COLORS['bg_light']};
            border-radius: {s(4)}px;
        }}
        QSlider::sub-page:horizontal {{
            background: {GRADIENTS['primary']};
            border-radius: {s(4)}px;
        }}
        QSlider::handle:horizontal {{
            background: {GRADIENTS['primary']};
            width: {s(22)}px;
            height: {s(22)}px;
            margin: -{s(7)}px 0;
            border-radius: {s(11)}px;
            border: {s(3)}px solid {COLORS['bg_white']};
        }}
        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
            border: {s(3)}px solid {COLORS['bg_light']};
        }}
    """


def get_table_style(scale_func=None):
    """获取表格样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QTableWidget {{
            gridline-color: {COLORS['border_light']};
            background-color: {COLORS['bg_white']};
            alternate-background-color: {COLORS['bg_light']};
            selection-background-color: rgba(102, 126, 234, 0.15);
            border: {s(1)}px solid {COLORS['border']};
            border-radius: {s(10)}px;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
        }}
        QTableWidget::item {{
            padding: {s(12)}px;
            border-bottom: {s(1)}px solid {COLORS['border_light']};
            color: {COLORS['text_dark']};
        }}
        QTableWidget::item:selected {{
            background-color: rgba(102, 126, 234, 0.2);
            color: {COLORS['primary']};
        }}
        QTableWidget::item:hover {{
            background-color: rgba(102, 126, 234, 0.08);
        }}
        QHeaderView::section {{
            background: {GRADIENTS['primary']};
            padding: {s(14)}px {s(12)}px;
            border: none;
            font-weight: bold;
            font-size: {s(14)}px;
            color: {COLORS['text_white']};
        }}
        QHeaderView::section:first {{
            border-top-left-radius: {s(10)}px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: {s(10)}px;
        }}
    """


def get_progress_bar_style(scale_func=None):
    """获取进度条样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QProgressBar {{
            border: none;
            border-radius: {s(10)}px;
            height: {s(20)}px;
            background: {COLORS['bg_light']};
            text-align: center;
            font-weight: bold;
            color: {COLORS['text_dark']};
        }}
        QProgressBar::chunk {{
            background: {GRADIENTS['primary']};
            border-radius: {s(10)}px;
        }}
    """


def get_groupbox_style(scale_func=None):
    """获取分组框样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QGroupBox {{
            font-size: {s(15)}px;
            font-weight: bold;
            color: {COLORS['text_dark']};
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            border: {s(2)}px solid {COLORS['border']};
            border-radius: {s(12)}px;
            margin-top: {s(12)}px;
            padding-top: {s(16)}px;
            background-color: {COLORS['bg_white']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {s(16)}px;
            padding: 0 {s(8)}px;
            background-color: {COLORS['bg_white']};
            color: {COLORS['primary']};
        }}
    """


def get_scrollbar_style(scale_func=None):
    """获取滚动条样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QScrollBar:vertical {{
            border: none;
            background: {COLORS['bg_light']};
            width: {s(10)}px;
            margin: 0;
            border-radius: {s(5)}px;
        }}
        QScrollBar::handle:vertical {{
            background: {GRADIENTS['primary']};
            min-height: {s(30)}px;
            border-radius: {s(5)}px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
            background: none;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {COLORS['bg_light']};
            height: {s(10)}px;
            margin: 0;
            border-radius: {s(5)}px;
        }}
        QScrollBar::handle:horizontal {{
            background: {GRADIENTS['primary']};
            min-width: {s(30)}px;
            border-radius: {s(5)}px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
            background: none;
        }}
    """


def get_tooltip_style(scale_func=None):
    """获取工具提示样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        QToolTip {{
            background: {GRADIENTS['primary']};
            color: {COLORS['text_white']};
            border: none;
            border-radius: {s(8)}px;
            padding: {s(8)}px {s(12)}px;
            font-size: {s(13)}px;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
        }}
    """


def get_message_box_style(variant='info'):
    """获取消息框样式"""
    colors = {
        'info': {'bg': '#e3f2fd', 'text': '#1976d2', 'border': '#90caf9'},
        'success': {'bg': '#e8f5e9', 'text': '#388e3c', 'border': '#a5d6a7'},
        'warning': {'bg': '#fff3e0', 'text': '#f57c00', 'border': '#ffcc80'},
        'error': {'bg': '#ffebee', 'text': '#d32f2f', 'border': '#ef9a9a'},
    }
    c = colors.get(variant, colors['info'])
    
    return f"""
        QMessageBox {{
            background-color: {c['bg']};
        }}
        QMessageBox QLabel {{
            color: {c['text']};
            font-size: 16px;
            font-weight: 500;
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            padding: 10px;
        }}
        QMessageBox QPushButton {{
            background: {GRADIENTS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: bold;
            min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['secondary_light']});
        }}
    """


# 全局应用样式
def get_global_style(scale_func=None):
    """获取全局应用样式"""
    s = scale_func if scale_func else lambda x: x
    
    return f"""
        * {{
            font-family: 'Microsoft YaHei', '微软雅黑', 'Segoe UI', Arial, sans-serif;
        }}
        QWidget {{
            background-color: {COLORS['bg_light']};
        }}
        QMainWindow {{
            background-color: {COLORS['bg_light']};
        }}
        {get_scrollbar_style(s)}
        {get_tooltip_style(s)}
    """
