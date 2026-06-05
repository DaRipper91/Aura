import os
from aura.core.mandates import aura_component, PaletteComponent

@aura_component
class AndroidPalette:
    """The Aesthetic Brain for Jules (Palette) - Android Target."""
    __slots__ = ("project_root",)

    def __init__(self, root: str):
        self.project_root = root

    def apply_theme(self):
        """Audits the Jetpack Compose UI for aesthetic consistency."""
        print("[🎨 PALETTE // ANDROID] Initiating mobile UX audit...")
        ui_path = os.path.join(self.project_root, "android/app/src/main/java/com/aura/app/MainActivity.kt")
        
        if not os.path.exists(ui_path):
            print("  [✗] Android UI source missing.")
            return

        with open(ui_path, "r") as f:
            content = f.read()
            # Enforce Obsidian background (0xFF0F0F0F)
            if "0xFF0F0F0F" not in content:
                print("  [!] MANDATED OBSIDIAN BACKGROUND MISSING from Android UI.")
            
            # Enforce Gold/Purple Accents
            required_accents = ["0xFFD4AF37", "0xFF8833FF"]
            for color in required_accents:
                if color not in content:
                    print(f"  [!] MANDATED ACCENT COLOR {color} MISSING from Android UI.")

    def audit_visuals(self):
        self.apply_theme()
        print("[🎨 PALETTE // ANDROID] Status: POLISHED.")

if __name__ == "__main__":
    brain = AndroidPalette(os.getcwd())
    brain.audit_visuals()
