#!/bin/bash
# DA-HP // MASTER INITIALIZATION SCRIPT

echo "🌌 Initializing Aura Logic Hub..."

# 1. Install CachyOS Keys
curl https://mirror.cachyos.org/cachyos-repo.tar.xz -o cachyos-repo.tar.xz
tar xvf cachyos-repo.tar.xz
./cachyos-repo.sh

# 2. Enable Services
systemctl enable --now tailscaled
systemctl enable --now cpupower
systemctl enable --now sshd

# 3. Global Agent Stack
npm install -g @google/gemini-cli
pip install aider-chat --break-system-packages

echo "✅ DA-HP Ready. SHUT UP AND COMPUTE."
