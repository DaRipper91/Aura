#!/bin/bash
# 🌲 DA-PINE // SUB-ROUTER BOOTSTRAP SCRIPT (Arch Linux ARM)
# Target: PinePhone (Original/Pro) - Barebone Headless
# Role: Layer 2 Wake-on-LAN Relay & Tailscale Subnet Router

set -e
trap 'echo "❌ ERROR: Bootstrap failed at line $LINENO"' ERR

echo "🌲 INITIALIZING DA-PINE BOOTSTRAP // SHUT UP AND COMPUTE."

# 1. HARDWARE OPTIMIZATION (Power & Heat Reduction)
echo "🔋 Disabling Mobile Hardware..."

# Disable Cellular Modem (Saves ~150mA and reduces heat)
if systemctl is-active --quiet eg25-manager; then
    systemctl disable --now eg25-manager
    echo "✅ EG25 Modem Manager disabled."
fi

# 2. SYSTEM TUNING
echo "⚡ Tuning sysctl for Routing..."
# Enable IP Forwarding for Tailscale Subnet Routing
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.d/99-tailscale.conf
sysctl -p /etc/sysctl.d/99-tailscale.conf

# 3. BASE PACKAGES
echo "📥 Installing Core Routing Packages..."
pacman -Syu --noconfirm
pacman -S --noconfirm tailscale fish openssh btop networkmanager

# 4. HARDENED SSH & USER SETUP
echo "🔑 Configuring SSH and Users..."
# The barebone image uses 'alarm', we'll set up 'daripper'
if ! id "daripper" &>/dev/null; then
    useradd -m -G wheel -s /usr/bin/fish daripper
fi
# Randomize root and alarm passwords
echo "root:$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)" | chpasswd
echo "alarm:$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)" | chpasswd

# Lock down SSH
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Sudoers
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel

# 5. TAILSCALE SETUP
echo "🚀 Enabling Services..."
systemctl enable --now NetworkManager sshd tailscaled

# Note: Authentication must be run manually or via TS_AUTH_KEY like Da-HP
if [ -n "$TS_AUTH_KEY" ]; then
    echo "🔗 Authenticating Tailscale as Subnet Router..."
    # Replace subnet with user's actual local subnet if known, default to a common one
    LOCAL_SUBNET="192.168.1.0/24" 
    tailscale up --authkey="$TS_AUTH_KEY" --hostname="Da-Pine" --ssh --advertise-routes="$LOCAL_SUBNET" --accept-routes
else
    echo "⚠️  No TS_AUTH_KEY provided. Manual routing required: 'tailscale up --advertise-routes=YOUR_SUBNET/24'"
fi

# 6. PERSISTENT SCREEN BLANKING
# The screen backlight stays on in tty. We use a systemd service to kill it on boot.
echo "🖥️ Configuring Headless Screen Blanking..."
cat <<EOF > /etc/systemd/system/pinephone-screen-off.service
[Unit]
Description=Disable PinePhone Backlight for Headless Mode
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 0 > /sys/class/backlight/backlight/brightness || true'

[Install]
WantedBy=multi-user.target
EOF
systemctl enable pinephone-screen-off.service

echo "✅ DA-PINE BOOTSTRAP COMPLETE."
echo "1. Reboot the device."
echo "2. SHUT UP AND COMPUTE."
