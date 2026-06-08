import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Aura: Local AI Interchange")
    parser.add_argument("prompt", nargs="*", help="Optional prompt to run in headless CLI mode")
    args, unknown = parser.parse_known_args()

    prompt = " ".join(args.prompt).strip()

    if prompt:
        # Headless CLI mode
        from aura_core.engine import OllamaClient
        client = OllamaClient()
        print(f"User: {prompt}")
        print("Aura: ", end="", flush=True)
        for chunk in client.autonomous_chat(client.current_model, prompt):
            print(chunk, end="", flush=True)
        print()
    else:
        # GUI mode
        from PySide6.QtWidgets import QApplication
        from aura.ui.window import AuraWindow
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        window = AuraWindow()
        window.show()
        
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
