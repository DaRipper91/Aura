import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 🛠️ MODULE DISCOVERY FIX:
# Add the python/ directory to the path so 'aura' and 'aura_core' are discoverable.
# We check if we're in a PyInstaller bundle or local dev.
if getattr(sys, 'frozen', False):
    # If frozen, 'python/' content was moved to root of _MEIPASS by our --paths flag
    sys.path.append(sys._MEIPASS)
else:
    # Local development
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
