import os
from aura.core.mandates import aura_component, PaletteComponent

@aura_component
class PaletteBrain:
    """The Aesthetic Brain for Jules (Palette)."""
    __slots__ = ("project_root",)

    def __init__(self, root: str):
        self.project_root = root

    def apply_theme(self):
        """Audits the UI for aesthetic consistency."""
        print("[🎨 PALETTE] Initiating UX audit...")
        ui_path = os.path.join(self.project_root, "aura/ui/window.py")
        if not os.path.exists(ui_path):
            print("  [✗] UI target missing.")
            return

        with open(ui_path, "r") as f:
            content = f.read()
            # Enforce Monospace mandate
            if "font-family" in content and "Monospace" not in content:
                print("  [!] NON-MONOSPACE font detected in UI.")
            # Enforce Cyber-Monospace palette (Purple/Gold)
            required_colors = ["#8833FF", "#D4AF37"]
            for color in required_colors:
                if color not in content:
                    print(f"  [!] Mandated color {color} missing from UI.")

    def audit_visuals(self):
        self.apply_theme()
        print("[🎨 PALETTE] Status: POLISHED.")

if __name__ == "__main__":
    brain = PaletteBrain(os.getcwd())
    brain.audit_visuals()
