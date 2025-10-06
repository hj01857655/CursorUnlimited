# -*- coding: utf-8 -*-
"""
UI Pages Module
"""

from .base_page import BasePage
from .dashboard_page import DashboardPage
from .accounts_page import AccountsPage
from .automation_page import AutomationPage
from .statistics_page import StatisticsPage
from .settings_page import SettingsPage
from .logs_page import LogsPage

__all__ = [
    'BasePage',
    'DashboardPage',
    'AccountsPage', 
    'AutomationPage',
    'StatisticsPage',
    'SettingsPage',
    'LogsPage'
]
