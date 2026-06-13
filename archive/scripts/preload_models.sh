#!/bin/bash
# Pre-loads Aura models into RAM/VRAM silently
echo "Starting Aura Pre-Loader..."

# Keep-alive is set to infinite (-1) via systemd, so this single request locks it in.
curl -X POST http://127.0.0.1:11434/api/generate -d '{"model": "aura-qwen:latest", "prompt": "", "stream": false}' > /dev/null 2>&1
echo "Aura-Qwen [LOADED]"

curl -X POST http://127.0.0.1:11434/api/generate -d '{"model": "aura-architect:latest", "prompt": "", "stream": false}' > /dev/null 2>&1
echo "Aura-Architect [LOADED]"

echo "Pre-load complete."
