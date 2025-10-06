# -*- coding: utf-8 -*-
"""
Main Window UI
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Window settings
        self.setWindowTitle("CursorUnlimited - Cursor账号管理工具")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Add tabs
        self.create_account_tab()
        self.create_automation_tab()
        self.create_settings_tab()
        
        # Status bar
        self.statusBar().showMessage("就绪")
        
        # Center window on screen
        self.center_window()
    
    def create_account_tab(self):
        """Create account management tab"""
        account_widget = QWidget()
        layout = QVBoxLayout(account_widget)
        
        # Header
        header = QLabel("<h2>账号管理</h2>")
        layout.addWidget(header)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_add = QPushButton("添加账号")
        btn_import = QPushButton("导入账号")
        btn_export = QPushButton("导出账号")
        btn_refresh = QPushButton("刷新列表")
        
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_import)
        button_layout.addWidget(btn_export)
        button_layout.addWidget(btn_refresh)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Placeholder for account list
        placeholder = QLabel("账号列表区域\n（待实现）")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("background-color: #f0f0f0; padding: 50px;")
        layout.addWidget(placeholder, 1)
        
        self.tabs.addTab(account_widget, "账号管理")
    
    def create_automation_tab(self):
        """Create automation control tab"""
        automation_widget = QWidget()
        layout = QVBoxLayout(automation_widget)
        
        # Header
        header = QLabel("<h2>自动化操作</h2>")
        layout.addWidget(header)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_auto_register = QPushButton("自动注册")
        btn_auto_login = QPushButton("自动登录")
        btn_switch_account = QPushButton("切换账号")
        btn_check_status = QPushButton("检查状态")
        
        button_layout.addWidget(btn_auto_register)
        button_layout.addWidget(btn_auto_login)
        button_layout.addWidget(btn_switch_account)
        button_layout.addWidget(btn_check_status)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Placeholder for automation controls
        placeholder = QLabel("自动化控制面板\n（待实现）")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("background-color: #f0f0f0; padding: 50px;")
        layout.addWidget(placeholder, 1)
        
        self.tabs.addTab(automation_widget, "自动化")
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Header
        header = QLabel("<h2>系统设置</h2>")
        layout.addWidget(header)
        
        # Placeholder for settings
        placeholder = QLabel("设置选项\n（待实现）")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("background-color: #f0f0f0; padding: 50px;")
        layout.addWidget(placeholder, 1)
        
        self.tabs.addTab(settings_widget, "设置")
    
    def center_window(self):
        """Center window on screen"""
        screen = self.screen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
