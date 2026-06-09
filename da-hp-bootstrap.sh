#!/bin/bash
# 🌌 DA-HP // GOD-MODE BOOTSTRAP SCRIPT (Arch Linux)
# Target: HP EliteDesk 800 G1 (i7-4790S)
# Authority: GEMA // THE MASTER

set -e

echo "🌌 INITIALIZING DA-HP BOOTSTRAP // SHUT UP AND COMPUTE."

# 1. DRIVE SELECTION (Surgical)
# Find the primary SSD. Priority: NVMe -> SATA
TARGET_DRIVE=$(lsblk -dno NAME,SIZE,TYPE | grep disk | grep -E "nvme|sd" | head -n 1 | awk '{print "/dev/"$1}')

if [ -z "$TARGET_DRIVE" ]; then
    echo "❌ ERROR: No target drive found."
    exit 1
fi

echo "🎯 TARGET_DRIVE: $TARGET_DRIVE"
if [[ "$1" != "--force" ]]; then
    read -p "⚠️  WARNING: This will WIPE $TARGET_DRIVE. Continue? (y/N): " confirm
    if [[ $confirm != "y" ]]; then exit 1; fi
fi

# 2. PARTITIONING (GPT)
echo "🏗️ Partitioning..."
sgdisk -Z $TARGET_DRIVE
sgdisk -n 1:0:+512M -t 1:ef00 -c 1:"EFI" $TARGET_DRIVE
sgdisk -n 2:0:0 -t 2:8300 -c 2:"ROOT" $TARGET_DRIVE

PART_EFI="${TARGET_DRIVE}1"
PART_ROOT="${TARGET_DRIVE}2"

# Handle NVMe naming convention (p1, p2)
if [[ $TARGET_DRIVE == *"nvme"* ]]; then
    PART_EFI="${TARGET_DRIVE}p1"
    PART_ROOT="${TARGET_DRIVE}p2"
fi

# 3. FORMATTING
echo "🧹 Formatting..."
mkfs.vfat -F 32 $PART_EFI
mkfs.ext4 -F $PART_ROOT

# 4. MOUNTING
mount $PART_ROOT /mnt
mkdir -p /mnt/boot
mount $PART_EFI /mnt/boot

# 5. PACSTRAP (Base Stack)
echo "📥 Pacstrapping Base System..."
pacstrap /mnt base base-devel linux-firmware git fish nodejs npm python python-pip tmux ripgrep fd tailscale openssh cpupower sudo btop

# 6. SYSTEM CONFIGURATION (Chroot)
echo "⚙️  Configuring Environment..."
genfstab -U /mnt >> /mnt/etc/fstab

arch-chroot /mnt /bin/bash <<EOF
set -e

# 6.1 PERSISTENT LOGGING
echo "📜 Enabling Persistent Journaling..."
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
sed -i 's/#Storage=auto/Storage=persistent/' /etc/systemd/journald.conf

# 7. CACHYOS INJECTION (Merged from User Base Script)
echo "⚡ Injecting CachyOS Repository..."
rm -rf /etc/pacman.d/cachyos-mirrorlist
pacman -Scc --noconfirm
cd /tmp
curl -O https://mirror.cachyos.org/cachyos-repo.tar.xz
tar xvf cachyos-repo.tar.xz
cd cachyos-repo
./cachyos-repo.sh
pacman -Syyu --noconfirm
pacman -S --noconfirm linux-cachyos linux-cachyos-headers

# 8. OPTIMIZATION: CPU Performance Governor
systemctl enable cpupower
mkdir -p /etc/systemd/system/cpupower.service.d/
cat <<EOT > /etc/systemd/system/cpupower.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/cpupower frequency-set -g performance
EOT

# 9. OPTIMIZATION: Huge Pages for LLM Inference
echo "vm.nr_hugepages = 1024" >> /etc/sysctl.d/99-ai-optimization.conf

# 10. BOOTLOADER (GRUB)
pacman -S --noconfirm grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg

# 11. USER & AGENT SETUP
if ! id "aura" &>/dev/null; then
    useradd -m -G wheel -s /usr/bin/fish aura
fi
echo "aura ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# 11.5 GLOBAL AGENT INSTALL
echo "📥 Installing Gemini CLI..."
npm install -g @google/gemini-cli

echo "📥 Installing Aider..."
pip install aider-chat --break-system-packages

# 11.6 OLLAMA INSTALLATION
echo "📥 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOT > /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Restart=always
RestartSec=3
EOT

# 11.7 OLLAMA WARMUP (Core Models)
echo "🔥 Warming up Ollama (Pulling Core Models)..."
systemctl start ollama
sleep 5
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:7b
ollama pull deepseek-coder-v2:16b

# 11.8 CUSTOM MODEL CREATION (Aura Suite)
echo "🏗️  Creating Custom Aura Models..."
# Note: These Modelfiles should be in /home/aura/ai-workspace/ollama/
# We assume the user clones the repo into ai-workspace
# For the bootstrap, we can pre-create them if the files exist in the chroot
mkdir -p /home/aura/ai-workspace/ollama
# [Logic for copying Modelfiles to the hub would go here, 
# but for now we'll ensure the bootstrap instructions mention it]

echo "👻 Ghost Protocol: SSH via Tailscale will be enabled on boot."

# 12. AI WORKSPACE & MANDATES
mkdir -p /home/aura/ai-workspace/logs
# Global Fish Env for Aura Agent
mkdir -p /home/aura/.config/fish/conf.d/
cat <<EOT > /home/aura/.config/fish/conf.d/aura_env.fish
set -gx GEMINI_CLI_APPROVAL_MODE yolo
set -gx GEMINI_CLI_OUTPUT_FORMAT text
set -gx PAGER cat
EOT

cat <<EOT > /home/aura/ai-workspace/GEMINI.md
# 🏛️ DA-HP // LOGIC HUB CONSTITUTION

## 🌌 IDENTITY & MISSION
- **Role:** GEMA // THE MASTER.
- **Environment:** Headless Arch Linux (EliteDesk i7-4790S).
- **Mission:** Autonomous repository management and God-Mode engineering.

## 🔐 AUTHENTICATION PROTOCOL (Google OAuth)
If gemini-cli requires login on this headless machine:
1. Run \`gemini login\` on DA-HP. Note the port (default 3000).
2. On your Command Deck (Mac), run: \`ssh -L 3000:localhost:3000 aura@<DA-HP-IP>\`
3. Open browser on Mac: \`http://localhost:3000\`
4. Complete login; token maps back to DA-HP automatically.

## 🏗️ OPERATIONAL MANDATES (SHUT UP AND COMPUTE)
1. **Satellite View:** Analyze the entire ~/ai-workspace before making code changes. 
2. **AVX2 Optimization:** Prioritize tools and libraries optimized for Haswell AVX2 instructions.
3. **Non-Interactive Execution:** Use --yes, --no-pager, and TIMEOUT wrappers. Never hang the terminal.
4. **Atomic Git:** Small, modular commits with technical rationale.
5. **No Slop:** Zero conversational filler. High-density technical output only.
6. **Resilience:** If services fail, check 'journalctl -u ollama' and 'tailscale status'.

## 🛠️ TOOLSET PREFERENCE
- **Core:** @google/gemini-cli
- **Shell:** Fish Shell (/usr/bin/fish)
- **Fixes:** aider (surgical multi-file edits)
- **Monitoring:** btop (CPU/RAM vitals)
- **Navigation:** fd, ripgrep, tmux

---
*DA-HP // SHUT UP AND COMPUTE.*
EOT

chown -R aura:aura /home/aura/

# 13. ENABLE SERVICES
systemctl enable sshd
systemctl enable tailscaled
systemctl enable ollama

EOF

echo "✅ DA-HP BOOTSTRAP COMPLETE."
echo "1. Reboot and login as 'aura'."
echo "2. Run 'sudo tailscale up --ssh' to join the hub."
echo "3. SHUT UP AND COMPUTE."
