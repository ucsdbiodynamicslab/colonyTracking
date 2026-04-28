"""Main GUI module - launches the PyQt6 application."""

import logging
import sys

logger = logging.getLogger(__name__)


def main():
    """Launch the GUI application."""
    logger.info("Colony Tracking System GUI launcher")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import Qt
    except ImportError:
        print("ERROR: PyQt6 not installed. Please install with: pip install PyQt6")
        sys.exit(1)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Colony Tracking System v1.0")
    window.setGeometry(100, 100, 800, 600)
    
    # Add placeholder label
    label = QLabel("Colony Tracking System\n\nGUI implementation in progress...\n\nFor now, use the Python API:\nfrom colonytracking import ColonyDetector, ColonyTracker")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    # Show window
    window.show()
    
    logger.info("GUI launched successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
