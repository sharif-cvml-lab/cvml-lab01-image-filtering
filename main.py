import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from gui import AppWindow

def main():
    # Setup high-DPI scaling for modern displays in PyQt6
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    window = AppWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
