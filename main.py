import sys
from PySide6.QtWidgets import QApplication
from aura.ui.window import AuraWindow
# Temporary fix for imports in subdirectories
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

def main():
    app = QApplication(sys.argv)
    
    # Modern look adjustments
    app.setStyle("Fusion")
    
    window = AuraWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
