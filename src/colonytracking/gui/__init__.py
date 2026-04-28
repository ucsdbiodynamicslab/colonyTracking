"""
Main GUI application for Colony Tracking System.

PyQt6-based graphical interface for interactive colony detection, tracking, and analysis.

To use the GUI, first install PyQt6:
    pip install colonytracking[gui]
"""

import logging
import sys

logger = logging.getLogger(__name__)


def main():
    """Launch the GUI application."""
    logger.info("Colony Tracking System GUI launcher")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt6.QtCore import Qt
    except ImportError:
        print("ERROR: PyQt6 not installed.")
        print("\nTo use the GUI, install with:")
        print("  pip install colonytracking[gui]")
        print("\nAlternatively, use the Python API for programmatic access:")
        print("  from colonytracking import ColonyDetector, ColonyTracker")
        sys.exit(1)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Colony Tracking System v1.0")
    window.setGeometry(100, 100, 900, 700)
    
    # Create central widget with layout
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Add information label
    info_text = """Colony Tracking System - Advanced Image Analysis Tool

FOR DOCUMENTATION AND QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Full documentation available at: https://github.com/biodynamics/colonytracking

🐍 Python API (Recommended for most users):
    from colonytracking import ColonyDetector, ColonyTracker, GrowthAnalysis
    
    # Load images and detect colonies
    detector = ColonyDetector()
    result = detector.detect(background_img, colony_img)
    
    # See docs/USAGE.md for complete examples

🎨 GUI Development In Progress:
    The PyQt6 GUI interface is under development.
    For now, use the Python API for all functionality.

✅ Features Currently Available:
   • Automatic colony detection with multi-stage filtering
   • Temporal tracking across frame sequences
   • Growth metric calculations (area, diameter, growth rates)
   • Publication-quality visualization (4 plot types)
   • Batch processing support
   • Comprehensive API documentation

📖 Getting Started:
   1. Install: pip install colonytracking[gui]
   2. Read docs/USAGE.md for examples
   3. Check docs/API.md for full API reference
   4. View docs/DEVELOPMENT.md for extending the system

Questions? See GitHub Issues: https://github.com/biodynamics/colonytracking/issues
"""
    
    label = QLabel(info_text)
    label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    label.setStyleSheet("padding: 20px; font-family: monospace; font-size: 10pt;")
    layout.addWidget(label)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Show window
    window.show()
    
    logger.info("GUI launched successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
