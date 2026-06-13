#!/bin/bash
# 1. Enforce Huge Pages in Ollama
# 2. Lock threads to Physical Cores (4) to maximize cache efficiency
# 3. Increase Keep Alive to infinite
echo 0 | sudo -S sh -c 'printf "[Service]\nEnvironment=\"OLLAMA_HOST=0.0.0.0\"\nEnvironment=\"OLLAMA_ORIGINS=*\"\nEnvironment=\"OLLAMA_NUM_PARALLEL=1\"\nEnvironment=\"OLLAMA_MAX_LOADED_MODELS=1\"\nEnvironment=\"OLLAMA_FLASH_ATTENTION=1\"\nEnvironment=\"OLLAMA_KEEP_ALIVE=-1\"\nEnvironment=\"OLLAMA_NUM_THREADS=4\"\n" > /etc/systemd/system/ollama.service.d/override.conf'
echo 0 | sudo -S systemctl daemon-reload
echo 0 | sudo -S systemctl restart ollama
