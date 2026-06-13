#!/bin/bash
echo 0 | sudo -S sh -c 'printf "[Service]\nEnvironment=\"OLLAMA_HOST=0.0.0.0\"\nEnvironment=\"OLLAMA_ORIGINS=*\"\nEnvironment=\"OLLAMA_NUM_PARALLEL=1\"\nEnvironment=\"OLLAMA_MAX_LOADED_MODELS=1\"\nEnvironment=\"OLLAMA_FLASH_ATTENTION=1\"\nEnvironment=\"OLLAMA_KEEP_ALIVE=24h\"\n" > /etc/systemd/system/ollama.service.d/override.conf'
echo 0 | sudo -S systemctl daemon-reload
echo 0 | sudo -S systemctl restart ollama
