#!/bin/bash
# 🌌 DA-HP // MASTER BOOTSTRAP SCRIPT (Arch Linux)
# Role: Arch Install Specialist // Optimized for Aura Logic Hub
# Target: HP EliteDesk 800 G1 (i7-4790S)
# Authority: GEMA // THE MASTER

set -e
trap 'echo "❌ ERROR: Bootstrap failed at line $LINENO"' ERR

echo "🌌 INITIALIZING DA-HP BOOTSTRAP // SHUT UP AND COMPUTE."

# 1. SURGICAL DRIVE SELECTION
# Exclude installation media and identify the primary disk
TARGET_DRIVE=$(lsblk -dno NAME,SIZE,TYPE,MOUNTPOINT | grep disk | grep -vE "airootfs|/" | sort -k2 -hr | head -n 1 | awk '{print "/dev/"$1}')

if [ -z "$TARGET_DRIVE" ]; then
    echo "❌ ERROR: No suitable target drive found."
    exit 1
fi

echo "🎯 TARGET_DRIVE: $TARGET_DRIVE (Optimized Alignment)"

# 2. PARTITIONING (GPT / UEFI / OPTIMAL)
echo "🏗️ Partitioning..."
wipefs -a "$TARGET_DRIVE"
parted -a optimal -s "$TARGET_DRIVE" mklabel gpt
parted -a optimal -s "$TARGET_DRIVE" mkpart "ESP" fat32 1MiB 1025MiB
parted -s "$TARGET_DRIVE" set 1 esp on
parted -a optimal -s "$TARGET_DRIVE" mkpart "primary" linux-swap 1025MiB 33GiB
parted -a optimal -s "$TARGET_DRIVE" mkpart "primary" ext4 33GiB 100%

# Define partitions dynamically
if [[ "$TARGET_DRIVE" == *"nvme"* ]]; then
    PART_EFI="${TARGET_DRIVE}p1"
    PART_SWAP="${TARGET_DRIVE}p2"
    PART_ROOT="${TARGET_DRIVE}p3"
else
    PART_EFI="${TARGET_DRIVE}1"
    PART_SWAP="${TARGET_DRIVE}2"
    PART_ROOT="${TARGET_DRIVE}3"
fi

# 3. FORMATTING
echo "🧹 Formatting..."
mkfs.vfat -F 32 "$PART_EFI"
mkswap "$PART_SWAP"
mkfs.ext4 -F "$PART_ROOT"

# 4. MOUNTING
echo "📂 Mounting..."
mount "$PART_ROOT" /mnt
mkdir -p /mnt/boot
mount "$PART_EFI" /mnt/boot
swapon "$PART_SWAP"

# 5. PACSTRAP (Performance Stack)
echo "📥 Pacstrapping Base System..."
pacstrap -K /mnt base base-devel linux-zen linux-zen-headers linux-firmware intel-ucode git fish nodejs npm python python-pip tmux ripgrep fd tailscale openssh cpupower sudo btop networkmanager fzf starship

# 6. SYSTEM CONFIGURATION (Chroot)
echo "⚙️  Configuring Environment..."
genfstab -U /mnt >> /mnt/etc/fstab

# Capture PARTUUID on the host to pass into chroot
ROOT_PARTUUID=$(blkid -s PARTUUID -o value "$PART_ROOT")

# Use 'EOF' to allow host variable expansion ($ROOT_PARTUUID)
arch-chroot /mnt /bin/bash <<EOF
set -e

# 6.1 LOCALIZATION & HOSTNAME
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
hwclock --systohc
echo "Da-HP" > /etc/hostname
cat <<EOT > /etc/hosts
127.0.0.1   localhost
::1         localhost
127.0.1.1   Da-HP.localdomain Da-HP
EOT

# 6.2 HARDENED SSH (Key-Only Preferred)
echo "🔑 Configuring SSH..."
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# 6.3 USER SETUP (daripper)
echo "👤 Creating user: daripper..."
if ! id "daripper" &>/dev/null; then
    useradd -m -G wheel -s /usr/bin/fish daripper
fi
echo "daripper:0" | chpasswd
# Randomize root password (unreachable via SSH)
echo "root:\$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)" | chpasswd
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel

# 6.4 SSH KEY INJECTION
mkdir -p /home/daripper/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC5m+MepSioIc0TmhMQRin1Px3DR3xGUmW7g3s+KFaRi daripper@Asahi" > /home/daripper/.ssh/authorized_keys
chown -R daripper:daripper /home/daripper/.ssh
chmod 700 /home/daripper/.ssh
chmod 600 /home/daripper/.ssh/authorized_keys

# 6.5 GEMINI-CLI INSTALLATION
echo "📥 Installing Gemini-CLI..."
npm install -g @google/gemini-cli

# 6.6 STARSHIP & FISH OPTIMIZATION
echo "🐟 Optimizing Fish Shell & Starship..."
mkdir -p /home/daripper/.config/fish
cat <<EOT > /home/daripper/.config/fish/config.fish
if status is-interactive
    starship init fish | source
end
set -g fish_greeting ""
alias aura="gemini"
EOT

# Download Aura Starship Config
curl -sL https://raw.githubusercontent.com/DaRipper91/Aura/main/configs/starship.toml -o /home/daripper/.config/starship.toml
chown -R daripper:daripper /home/daripper/.config

# 6.7 AUTO-LOGIN (tty1)
echo "🤖 Enabling Auto-Login..."
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat <<EOT > /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin daripper --noclear %I \\\$TERM
EOT

# 7. BOOTLOADER (systemd-boot)
echo "🚜 Installing systemd-boot..."
bootctl install

echo "⚙️ Configuring boot loader..."
cat <<EOT > /boot/loader/loader.conf
default arch.conf
timeout 3
console-mode max
editor no
EOT

echo "⚙️ Creating Arch Linux boot entry..."
cat <<EOT > /boot/loader/entries/arch.conf
title   Arch Linux (Zen)
linux   /vmlinuz-linux-zen
initrd  /intel-ucode.img
initrd  /initramfs-linux-zen.img
options root=PARTUUID=$ROOT_PARTUUID rw quiet intel_iommu=on intel_pstate=active audit=0
EOT

# 8. PERFORMANCE & PERSISTENCE
echo "⚡ Tuning for LLM Workloads..."
systemctl enable cpupower
systemctl enable fstrim.timer

# Advanced Sysctl Tuning (RAM Dependent)
TOTAL_RAM_KB=\$(grep MemTotal /proc/meminfo | awk '{print \$2}')
if [ "\$TOTAL_RAM_KB" -gt 8000000 ]; then
    echo "🚀 High RAM detected. Enabling Huge Pages..."
    cat <<EOT > /etc/sysctl.d/99-ai-optimization.conf
vm.nr_hugepages = 1024
vm.swappiness = 10
fs.file-max = 2097152
EOT
else
    echo "⚠️  Low RAM detected. Skipping Huge Pages to prevent OOM."
    cat <<EOT > /etc/sysctl.d/99-ai-optimization.conf
vm.swappiness = 10
fs.file-max = 2097152
EOT
fi

# HP-WMI Blacklist Persistence
echo "blacklist hp-wmi" > /etc/modprobe.d/hp.conf

# 9. SERVICES
echo "🚀 Enabling Services..."
systemctl enable NetworkManager sshd tailscaled

# 9.2 WIFI PRE-CONFIGURATION (File-based)
mkdir -p /etc/NetworkManager/system-connections/

# Logic to pick the best interface: prefer wlan1, fallback to any wl*
WIFI_IFACE=\$(ls /sys/class/net | grep -E "^wlan1|^wl" | sort -r | head -n 1 || true)

if [ -n "\$WIFI_IFACE" ]; then
    echo "📡 Configuring WiFi for interface: \$WIFI_IFACE"
    cat <<EOT > /etc/NetworkManager/system-connections/Aura-WiFi.nmconnection
[connection]
id=Aura-WiFi
type=wifi
interface-name=\$WIFI_IFACE
autoconnect=true

[wifi]
mode=infrastructure
ssid=ADND2.4

[wifi-security]
key-mgmt=wpa-psk
psk=SunShine42?!?

[ipv4]
method=auto

[ipv6]
method=auto
EOT
    chmod 600 /etc/NetworkManager/system-connections/Aura-WiFi.nmconnection
fi

EOF

# 10. HOST-SIDE TAILSCALE AUTH (If key provided)
if [ -n "$TS_AUTH_KEY" ]; then
    echo "🔗 Authenticating Tailscale with Auth Key..."
    arch-chroot /mnt /bin/bash -c "tailscaled --tun=userspace-networking & sleep 5 && tailscale up --authkey=$TS_AUTH_KEY --hostname=Da-HP --ssh && killall tailscaled" || true
fi

echo "✅ DA-HP BOOTSTRAP COMPLETE."
echo "1. Reboot: 'umount -R /mnt && reboot'"
echo "2. SHUT UP AND COMPUTE."
