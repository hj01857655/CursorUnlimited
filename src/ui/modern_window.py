# -*- coding: utf-8 -*-
"""
现代化主窗口 - 侧边导航设计
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QScrollArea
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QColor, QPalette


class SideNavButton(QPushButton):
    """侧边导航按钮"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.icon_text = icon_text
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style(False)
    
    def apply_style(self, is_active):
        """应用样式"""
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-left: 4px solid #1976D2;
                    text-align: left;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1E88E5;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #333;
                    border: none;
                    text-align: left;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                }
            """)
    
    def setActive(self, active):
        """设置激活状态"""
        self.setChecked(active)
        self.apply_style(active)


class ModernMainWindow(QMainWindow):
    """现代化主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_page = 0
    
    def init_ui(self):
        """初始化UI"""
        # 窗口设置
        self.setWindowTitle("CursorUnlimited - Cursor账号管理工具")
        self.setMinimumSize(1400, 900)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（水平）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏
        self.create_sidebar(main_layout)
        
        # 创建右侧内容区域
        self.create_content_area(main_layout)
        
        # 应用全局样式
        self.apply_global_style()
        
        # 窗口居中
        self.center_window()
    
    def create_sidebar(self, parent_layout):
        """创建侧边导航栏"""
        # 侧边栏容器
        sidebar = QFrame()
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-right: 1px solid #E0E0E0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo区域
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 30, 20, 30)
        
        logo_label = QLabel("CursorUnlimited")
        logo_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2196F3;
        """)
        logo_layout.addWidget(logo_label)
        
        version_label = QLabel("v0.1.0")
        version_label.setStyleSheet("font-size: 12px; color: #999;")
        logo_layout.addWidget(version_label)
        
        sidebar_layout.addWidget(logo_widget)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E0E0E0;")
        sidebar_layout.addWidget(line)
        
        # 导航按钮
        self.nav_buttons = []
        
        nav_items = [
            ("🏠 首页", "dashboard"),
            ("👤 账号管理", "accounts"),
            ("🤖 自动化", "automation"),
            ("📊 数据统计", "statistics"),
            ("⚙️ 设置", "settings"),
            ("📝 日志", "logs"),
        ]
        
        for text, _ in nav_items:
            btn = SideNavButton(text)
            btn.clicked.connect(lambda checked, idx=len(self.nav_buttons): self.switch_page(idx))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        # 设置第一个按钮为激活状态
        if self.nav_buttons:
            self.nav_buttons[0].setActive(True)
        
        # 底部空白区域
        sidebar_layout.addStretch()
        
        # 底部信息
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(20, 10, 20, 20)
        
        status_label = QLabel("● 已连接")
        status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        status_layout.addWidget(status_label)
        
        sidebar_layout.addWidget(status_widget)
        
        parent_layout.addWidget(sidebar)
    
    def create_content_area(self, parent_layout):
        """创建内容区域"""
        # 内容区域容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 顶部标题栏
        self.create_title_bar(content_layout)
        
        # 页面堆栈
        self.page_stack = QStackedWidget()
        content_layout.addWidget(self.page_stack)
        
        # 添加各个页面
        from .pages.dashboard_page import DashboardPage
        from .pages.accounts_page import AccountsPage
        from .pages.automation_page import AutomationPage
        from .pages.statistics_page import StatisticsPage
        from .pages.settings_page import SettingsPage
        from .pages.logs_page import LogsPage
        
        self.page_stack.addWidget(DashboardPage())
        self.page_stack.addWidget(AccountsPage())
        self.page_stack.addWidget(AutomationPage())
        self.page_stack.addWidget(StatisticsPage())
        self.page_stack.addWidget(SettingsPage())
        self.page_stack.addWidget(LogsPage())
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
                color: #666;
            }
        """)
        
        parent_layout.addWidget(content_container, 1)
    
    def create_title_bar(self, parent_layout):
        """创建标题栏"""
        title_bar = QWidget()
        title_bar.setMinimumHeight(60)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(30, 10, 30, 10)
        
        # 页面标题
        self.page_title = QLabel("首页")
        self.page_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
        """)
        title_layout.addWidget(self.page_title)
        
        title_layout.addStretch()
        
        # 右侧工具按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet(self.get_tool_button_style())
        refresh_btn.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(refresh_btn)
        
        help_btn = QPushButton("❓ 帮助")
        help_btn.setStyleSheet(self.get_tool_button_style())
        help_btn.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(help_btn)
        
        parent_layout.addWidget(title_bar)
    
    def get_tool_button_style(self):
        """获取工具按钮样式"""
        return """
            QPushButton {
                background-color: transparent;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                color: #666;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #2196F3;
                color: #2196F3;
            }
        """
    
    def switch_page(self, index):
        """切换页面"""
        # 更新导航按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.setActive(i == index)
        
        # 切换页面
        self.page_stack.setCurrentIndex(index)
        self.current_page = index
        
        # 更新标题
        titles = ["首页", "账号管理", "自动化", "数据统计", "设置", "日志"]
        if index < len(titles):
            self.page_title.setText(titles[index])
    
    def apply_global_style(self):
        """应用全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
            }
        """)
    
    def center_window(self):
        """窗口居中"""
        screen = self.screen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
