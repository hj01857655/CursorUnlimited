# -*- coding: utf-8 -*-
"""
页面基类
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt


class BasePage(QWidget):
    """页面基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI - 子类重写"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 子类可以添加内容
        self.setup_content(layout)
    
    def setup_content(self, layout):
        """设置内容 - 子类必须实现"""
        placeholder = QLabel("页面内容")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            font-size: 16px;
            color: #999;
            padding: 50px;
        """)
        layout.addWidget(placeholder)
