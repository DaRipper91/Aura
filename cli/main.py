import sys
import os

# Ensure the CLI can find the core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import AuraEngine

def main():
    """
    The Linux TUI/CLI Entry Point.
    Handles terminal standard I/O and text formatting.
    """
    engine = AuraEngine()
    print("🌌 AURA CLI IS ONLINE. TYPE 'exit' TO QUIT.")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit']: 
                print("Disconnecting from the void...")
                break
            
            sys.stdout.write("AURA: ")
            sys.stdout.flush()
            
            # Consume the core engine's generator
            for chunk in engine.stream_chat(user_input):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print()
            
        except KeyboardInterrupt:
            print("\nDisconnecting from the void...")
            break

if __name__ == "__main__":
    main()
