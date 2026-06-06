import sys
import os

# Add the python/ directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))

from aura.ui.window import AuraWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = AuraWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
