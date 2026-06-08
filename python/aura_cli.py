#!/usr/bin/env python3
import sys
import os
import argparse

# Add python/ to path for internal modules
sys.path.append(os.path.join(os.path.dirname(__file__), "python"))

from aura_core.engine import OllamaClient

def run_cli():
    parser = argparse.ArgumentParser(description="Aura CLI: Local AI Autonomous Agent")
    parser.add_argument("prompt", nargs="?", help="Initial prompt to start the session")
    parser.add_argument("--model", default="qwen2.5-coder:1.5b", help="Ollama model to use")
    parser.add_argument("--verbosity", type=float, default=0.5, help="Response verbosity (0.0 to 1.0)")
    args = parser.parse_args()

    client = OllamaClient()
    client.set_verbosity(args.verbosity)
    
    # Verify Ollama connection
    if not client.scan_integrity():
        print("❌ Error: Could not connect to Ollama. Is it running?")
        sys.exit(1)

    print(f"🌌 Aura CLI Initialized // Model: {args.model}")
    print("Type 'exit' or 'quit' to end the session.\n")

    initial_prompt = args.prompt
    
    while True:
        if initial_prompt:
            user_input = initial_prompt
            initial_prompt = None
        else:
            try:
                user_input = input(">>> ").strip()
            except EOFError:
                break

        if user_input.lower() in ["exit", "quit"]:
            break
            
        if user_input.startswith("cd "):
            target = user_input[3:].strip()
            if target == "~":
                target = os.path.expanduser("~")
            new_path = os.path.normpath(os.path.join(client.project_root, target))
            if os.path.isdir(new_path):
                client.project_root = new_path
                print(f"📂 Context shifted to: {new_path}")
                if client.project_context:
                    print("✨ Project context loaded.")
            else:
                print(f"❌ Error: Directory not found: {target}")
            continue

        if not user_input:
            continue

        # Run the autonomous loop
        try:
            for chunk in client.autonomous_chat(model=args.model, prompt=user_input):
                print(chunk, end="", flush=True)
            print("\n")
        except KeyboardInterrupt:
            print("\n[Interrupted]")
            continue

if __name__ == "__main__":
    run_cli()
