import sys
import os

# Add the python/ directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))

from aura.ui.window import AuraWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Handle Target-specific logic (Xbox / Desktop)
    target = os.environ.get("AURA_TARGET", "DESKTOP")
    is_console = "--console" in sys.argv or target == "XBOX"
    
    window = AuraWindow()
    if is_console:
        window.showFullScreen()
    else:
        window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
