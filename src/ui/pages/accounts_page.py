# -*- coding: utf-8 -*-
"""
账号管理页面
"""

import json
import csv
from datetime import datetime
from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMenu, QMessageBox, QFileDialog,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QLabel, QGroupBox, QSplitter, QToolBar,
    QAbstractItemView, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QAction, QIcon, QColor

from ...services.database_manager import DatabaseManager
from ...services.account_switcher import AccountSwitcher
from ...models.account import AccountStatus
from ...utils.logger import setup_logger


class AccountDialog(QDialog):
    """账号添加/编辑对话框"""
    
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.account = account
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑账号" if self.account else "添加账号")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@gmail.com")
        basic_layout.addRow("邮箱:", self.email_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("可选，用于自动登录")
        basic_layout.addRow("密码:", self.password_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("可选")
        basic_layout.addRow("用户名:", self.username_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Token信息组
        token_group = QGroupBox("认证信息")
        token_layout = QFormLayout()
        
        self.access_token_edit = QTextEdit()
        self.access_token_edit.setMaximumHeight(60)
        self.access_token_edit.setPlaceholderText("访问令牌")
        token_layout.addRow("Access Token:", self.access_token_edit)
        
        self.refresh_token_edit = QTextEdit()
        self.refresh_token_edit.setMaximumHeight(60)
        self.refresh_token_edit.setPlaceholderText("刷新令牌（可选）")
        token_layout.addRow("Refresh Token:", self.refresh_token_edit)
        
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
        # 其他信息组
        other_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in AccountStatus])
        other_layout.addRow("状态:", self.status_combo)
        
        self.is_active_check = QCheckBox("启用账号")
        self.is_active_check.setChecked(True)
        other_layout.addRow("", self.is_active_check)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText("备注信息")
        other_layout.addRow("备注:", self.notes_edit)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("标签，用逗号分隔")
        other_layout.addRow("标签:", self.tags_edit)
        
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.cancelled.connect(self.reject)
        layout.addWidget(buttons)
        
        # 如果是编辑模式，填充数据
        if self.account:
            self.load_account_data()
    
    def load_account_data(self):
        """加载账号数据"""
        if not self.account:
            return
            
        self.email_edit.setText(self.account.email)
        self.email_edit.setReadOnly(True)  # 邮箱不允许修改
        
        if self.account.password:
            self.password_edit.setText(self.account.password)
        if self.account.username:
            self.username_edit.setText(self.account.username)
        if self.account.access_token:
            self.access_token_edit.setText(self.account.access_token)
        if self.account.refresh_token:
            self.refresh_token_edit.setText(self.account.refresh_token)
        if self.account.status:
            self.status_combo.setCurrentText(self.account.status.value)
        
        self.is_active_check.setChecked(self.account.is_active)
        
        if self.account.notes:
            self.notes_edit.setText(self.account.notes)
        if self.account.tags:
            self.tags_edit.setText(self.account.tags)
    
    def get_account_data(self) -> Dict:
        """获取账号数据"""
        return {
            'email': self.email_edit.text().strip(),
            'password': self.password_edit.text(),
            'username': self.username_edit.text().strip(),
            'access_token': self.access_token_edit.toPlainText().strip(),
            'refresh_token': self.refresh_token_edit.toPlainText().strip(),
            'status': AccountStatus(self.status_combo.currentText()),
            'is_active': self.is_active_check.isChecked(),
            'notes': self.notes_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip()
        }


class AccountSwitchThread(QThread):
    """账号切换线程"""
    finished = Signal(bool, str)
    
    def __init__(self, switcher, account_id):
        super().__init__()
        self.switcher = switcher
        self.account_id = account_id
    
    def run(self):
        """执行切换"""
        success, message = self.switcher.switch_account(self.account_id)
        self.finished.emit(success, message)


class AccountsPage(QWidget):
    """账号管理页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger("AccountsPage")
        self.db_manager = DatabaseManager()
        self.account_switcher = AccountSwitcher(self.db_manager)
        self.current_account_id = None
        self.init_ui()
        self.load_accounts()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_current_status)
        self.refresh_timer.start(5000)  # 每5秒刷新一次状态
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 添加按钮
        self.btn_add = QPushButton("➕ 添加账号")
        self.btn_add.clicked.connect(self.add_account)
        toolbar_layout.addWidget(self.btn_add)
        
        self.btn_import = QPushButton("📥 导入")
        self.btn_import.clicked.connect(self.import_accounts)
        toolbar_layout.addWidget(self.btn_import)
        
        self.btn_export = QPushButton("📤 导出")
        self.btn_export.clicked.connect(self.export_accounts)
        toolbar_layout.addWidget(self.btn_export)
        
        self.btn_sync = QPushButton("🔄 同步当前")
        self.btn_sync.setToolTip("将当前Cursor中的账号同步到数据库")
        self.btn_sync.clicked.connect(self.sync_current_account)
        toolbar_layout.addWidget(self.btn_sync)
        
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self.load_accounts)
        toolbar_layout.addWidget(self.btn_refresh)
        
        toolbar_layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("共 0 个账号")
        toolbar_layout.addWidget(self.stats_label)
        
        layout.addLayout(toolbar_layout)
        
        # 账号表格
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        
        # 设置列
        columns = [
            "ID", "邮箱", "用户名", "状态", "类型", 
            "配额", "已用", "剩余", "最后登录", 
            "备注", "操作"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 200)  # 邮箱
        self.table.setColumnWidth(2, 100)  # 用户名
        self.table.setColumnWidth(3, 80)   # 状态
        self.table.setColumnWidth(4, 60)   # 类型
        self.table.setColumnWidth(5, 80)   # 配额
        self.table.setColumnWidth(6, 80)   # 已用
        self.table.setColumnWidth(7, 80)   # 剩余
        self.table.setColumnWidth(8, 150)  # 最后登录
        self.table.setColumnWidth(9, 200)  # 备注
        header.setSectionResizeMode(10, QHeaderView.Stretch)  # 操作列自适应
        
        # 隐藏ID列
        self.table.setColumnHidden(0, True)
        
        layout.addWidget(self.table)
        
        # 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.current_account_label = QLabel("当前账号: 未登录")
        status_layout.addWidget(self.current_account_label)
        
        layout.addLayout(status_layout)
    
    def load_accounts(self):
        """加载账号列表"""
        try:
            self.logger.info("加载账号列表")
            accounts = self.db_manager.get_all_accounts()
            
            self.table.setRowCount(len(accounts))
            
            for row, account in enumerate(accounts):
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(account.id)))
                
                # 邮箱
                email_item = QTableWidgetItem(account.email)
                if account.is_primary:
                    email_item.setText(f"⭐ {account.email}")
                    email_item.setForeground(QColor("#FF6B00"))
                self.table.setItem(row, 1, email_item)
                
                # 用户名
                self.table.setItem(row, 2, QTableWidgetItem(account.username or "-"))
                
                # 状态
                status_item = QTableWidgetItem(account.status.value if account.status else "未知")
                if account.status == AccountStatus.ACTIVE:
                    status_item.setForeground(QColor("green"))
                elif account.status == AccountStatus.EXPIRED:
                    status_item.setForeground(QColor("red"))
                elif account.status == AccountStatus.ERROR:
                    status_item.setForeground(QColor("orange"))
                self.table.setItem(row, 3, status_item)
                
                # 类型（主账号/子账号）
                type_text = "主账号" if account.is_primary else "子账号"
                self.table.setItem(row, 4, QTableWidgetItem(type_text))
                
                # 配额
                quota_text = f"{account.total_quota:.2f}" if account.total_quota > 0 else "无限"
                self.table.setItem(row, 5, QTableWidgetItem(quota_text))
                
                # 已用
                self.table.setItem(row, 6, QTableWidgetItem(f"{account.used_quota:.2f}"))
                
                # 剩余
                remaining_text = f"{account.remaining_quota:.2f}" if account.total_quota > 0 else "无限"
                remaining_item = QTableWidgetItem(remaining_text)
                if account.total_quota > 0 and account.quota_percentage > 80:
                    remaining_item.setForeground(QColor("red"))
                self.table.setItem(row, 7, remaining_item)
                
                # 最后登录
                last_login = account.last_login_at.strftime("%Y-%m-%d %H:%M") if account.last_login_at else "从未"
                self.table.setItem(row, 8, QTableWidgetItem(last_login))
                
                # 备注
                self.table.setItem(row, 9, QTableWidgetItem(account.notes or ""))
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 0, 5, 0)
                
                btn_switch = QPushButton("切换")
                btn_switch.setMaximumWidth(60)
                btn_switch.clicked.connect(lambda checked, aid=account.id: self.switch_account(aid))
                btn_layout.addWidget(btn_switch)
                
                btn_edit = QPushButton("编辑")
                btn_edit.setMaximumWidth(60)
                btn_edit.clicked.connect(lambda checked, aid=account.id: self.edit_account(aid))
                btn_layout.addWidget(btn_edit)
                
                self.table.setCellWidget(row, 10, btn_widget)
                
                # 设置行高
                self.table.setRowHeight(row, 35)
                
                # 如果账号被禁用，设置行背景色
                if not account.is_active:
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(240, 240, 240))
            
            # 更新统计信息
            stats = self.db_manager.get_statistics()
            self.stats_label.setText(
                f"共 {stats['total_accounts']} 个账号 | "
                f"活跃: {stats['active_accounts']} | "
                f"禁用: {stats['inactive_accounts']}"
            )
            
            self.status_label.setText(f"已加载 {len(accounts)} 个账号")
            self.logger.info(f"加载完成，共 {len(accounts)} 个账号")
            
        except Exception as e:
            self.logger.error(f"加载账号失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"加载账号失败: {str(e)}")
    
    def refresh_current_status(self):
        """刷新当前账号状态"""
        try:
            current = self.account_switcher.get_current_account()
            if current:
                self.current_account_label.setText(f"当前账号: {current.email}")
                self.current_account_id = current.id
            else:
                self.current_account_label.setText("当前账号: 未登录")
                self.current_account_id = None
        except Exception as e:
            self.logger.error(f"刷新状态失败: {str(e)}")
    
    def add_account(self):
        """添加账号"""
        dialog = AccountDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_account_data()
            
            if not data['email']:
                QMessageBox.warning(self, "警告", "请输入邮箱地址")
                return
            
            try:
                account = self.db_manager.add_account(**data)
                if account:
                    self.load_accounts()
                    QMessageBox.information(self, "成功", f"账号 {data['email']} 添加成功")
                else:
                    QMessageBox.warning(self, "警告", f"账号 {data['email']} 已存在")
            except Exception as e:
                self.logger.error(f"添加账号失败: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "错误", f"添加账号失败: {str(e)}")
    
    def edit_account(self, account_id: int):
        """编辑账号"""
        account = self.db_manager.get_account(account_id)
        if not account:
            QMessageBox.warning(self, "警告", "账号不存在")
            return
        
        dialog = AccountDialog(self, account)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_account_data()
            
            try:
                if self.db_manager.update_account(account_id, **data):
                    self.load_accounts()
                    QMessageBox.information(self, "成功", "账号更新成功")
                else:
                    QMessageBox.warning(self, "警告", "账号更新失败")
            except Exception as e:
                self.logger.error(f"更新账号失败: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "错误", f"更新账号失败: {str(e)}")
    
    def delete_account(self, account_id: int):
        """删除账号"""
        account = self.db_manager.get_account(account_id)
        if not account:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除账号 {account.email} 吗？\n此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_account(account_id):
                    self.load_accounts()
                    QMessageBox.information(self, "成功", "账号删除成功")
                else:
                    QMessageBox.warning(self, "警告", "账号删除失败")
            except Exception as e:
                self.logger.error(f"删除账号失败: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "错误", f"删除账号失败: {str(e)}")
    
    def switch_account(self, account_id: int):
        """切换账号"""
        reply = QMessageBox.question(
            self, "确认切换",
            "切换账号将关闭Cursor进程，是否继续？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.status_label.setText("正在切换账号...")
            
            # 使用线程执行切换
            self.switch_thread = AccountSwitchThread(self.account_switcher, account_id)
            self.switch_thread.finished.connect(self.on_switch_finished)
            self.switch_thread.start()
    
    def on_switch_finished(self, success: bool, message: str):
        """切换完成回调"""
        if success:
            QMessageBox.information(self, "成功", message)
            self.load_accounts()
            self.refresh_current_status()
        else:
            QMessageBox.critical(self, "错误", message)
        
        self.status_label.setText("就绪")
    
    def set_primary(self, account_id: int):
        """设置主账号"""
        try:
            if self.db_manager.set_primary_account(account_id):
                self.load_accounts()
                QMessageBox.information(self, "成功", "主账号设置成功")
            else:
                QMessageBox.warning(self, "警告", "设置主账号失败")
        except Exception as e:
            self.logger.error(f"设置主账号失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"设置主账号失败: {str(e)}")
    
    def toggle_active(self, account_id: int):
        """切换启用/禁用状态"""
        account = self.db_manager.get_account(account_id)
        if not account:
            return
        
        try:
            new_status = not account.is_active
            if self.db_manager.update_account(account_id, is_active=new_status):
                self.load_accounts()
                status_text = "启用" if new_status else "禁用"
                QMessageBox.information(self, "成功", f"账号已{status_text}")
            else:
                QMessageBox.warning(self, "警告", "操作失败")
        except Exception as e:
            self.logger.error(f"切换状态失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
    
    def sync_current_account(self):
        """同步当前账号"""
        self.status_label.setText("正在同步...")
        
        try:
            success, message = self.account_switcher.sync_current_account()
            if success:
                self.load_accounts()
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "警告", message)
        except Exception as e:
            self.logger.error(f"同步失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"同步失败: {str(e)}")
        finally:
            self.status_label.setText("就绪")
    
    def import_accounts(self):
        """导入账号"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "",
            "JSON文件 (*.json);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
            elif file_path.endswith('.csv'):
                accounts_data = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        accounts_data.append(row)
            else:
                QMessageBox.warning(self, "警告", "不支持的文件格式")
                return
            
            count = self.db_manager.import_accounts(accounts_data)
            self.load_accounts()
            QMessageBox.information(self, "成功", f"成功导入 {count} 个账号")
            
        except Exception as e:
            self.logger.error(f"导入失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
    
    def export_accounts(self):
        """导出账号"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存导出文件", "accounts.json",
            "JSON文件 (*.json);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            accounts_data = self.db_manager.export_accounts()
            
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(accounts_data, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.csv'):
                if accounts_data:
                    with open(file_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=accounts_data[0].keys())
                        writer.writeheader()
                        writer.writerows(accounts_data)
            
            QMessageBox.information(self, "成功", f"成功导出 {len(accounts_data)} 个账号")
            
        except Exception as e:
            self.logger.error(f"导出失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.table.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        account_id = int(self.table.item(row, 0).text())
        account = self.db_manager.get_account(account_id)
        
        if not account:
            return
        
        menu = QMenu(self)
        
        # 切换账号
        action_switch = menu.addAction("🔄 切换到此账号")
        action_switch.triggered.connect(lambda: self.switch_account(account_id))
        
        menu.addSeparator()
        
        # 编辑
        action_edit = menu.addAction("✏️ 编辑")
        action_edit.triggered.connect(lambda: self.edit_account(account_id))
        
        # 设为主账号
        if not account.is_primary:
            action_primary = menu.addAction("⭐ 设为主账号")
            action_primary.triggered.connect(lambda: self.set_primary(account_id))
        
        # 启用/禁用
        if account.is_active:
            action_toggle = menu.addAction("🚫 禁用账号")
        else:
            action_toggle = menu.addAction("✅ 启用账号")
        action_toggle.triggered.connect(lambda: self.toggle_active(account_id))
        
        menu.addSeparator()
        
        # 复制信息
        copy_menu = menu.addMenu("📋 复制")
        
        action_copy_email = copy_menu.addAction("邮箱")
        action_copy_email.triggered.connect(
            lambda: QApplication.clipboard().setText(account.email)
        )
        
        if account.access_token:
            action_copy_token = copy_menu.addAction("Access Token")
            action_copy_token.triggered.connect(
                lambda: QApplication.clipboard().setText(account.access_token)
            )
        
        menu.addSeparator()
        
        # 删除
        action_delete = menu.addAction("🗑️ 删除")
        action_delete.triggered.connect(lambda: self.delete_account(account_id))
        
        menu.exec(self.table.mapToGlobal(pos))
    
    def on_item_double_click(self, item):
        """双击表格项"""
        if item.column() == 1:  # 双击邮箱列切换账号
            row = item.row()
            account_id = int(self.table.item(row, 0).text())
            self.switch_account(account_id)
        elif item.column() in [2, 3, 9]:  # 双击其他列编辑
            row = item.row()
            account_id = int(self.table.item(row, 0).text())
            self.edit_account(account_id)