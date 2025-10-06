#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CursorUnlimited - Cursor AI Account Management Tool
Main Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.utils.config import Config


def main():
    """Application entry point"""
    # Initialize logger
    logger = setup_logger()
    logger.info("Starting CursorUnlimited application...")
    
    # Load configuration
    config = Config()
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("CursorUnlimited")
    app.setOrganizationName("CursorUnlimited")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
