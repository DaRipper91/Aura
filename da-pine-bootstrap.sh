#!/bin/bash
# 🌲 DA-PINE // SUB-ROUTER BOOTSTRAP SCRIPT (Fedora 44 Mobile)
# Target: PinePhone (Original/Pro) - Fedora Mobile
# Role: Layer 2 Wake-on-LAN Relay & Tailscale Subnet Router

set -e
trap 'echo "❌ ERROR: Bootstrap failed at line $LINENO"' ERR

echo "🌲 INITIALIZING DA-PINE BOOTSTRAP (Fedora) // SHUT UP AND COMPUTE."

# 1. GUI ASSASSINATION (Freeing RAM)
echo "🗡️  Disabling Graphical Environment..."
# Fedora Mobile uses Plasma Mobile or Phosh. We kill both and switch to multi-user target (tty).
systemctl set-default multi-user.target
systemctl stop sddm || systemctl stop phosh || true
echo "✅ GUI disabled. System will now boot to a headless terminal."

# 2. HARDWARE OPTIMIZATION
echo "🔋 Killing unnecessary mobile hardware..."
# Disable Modem (Saves heat/power)
if systemctl is-active --quiet eg25-manager; then
    systemctl disable --now eg25-manager
    echo "✅ EG25 Modem Manager disabled."
fi

# 3. SYSTEM TUNING
echo "⚡ Tuning sysctl for Routing..."
# Enable IP Forwarding
cat <<EOF > /etc/sysctl.d/99-tailscale.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
sysctl -p /etc/sysctl.d/99-tailscale.conf

# 4. BASE PACKAGES (Fedora / DNF)
echo "📥 Installing Core Routing Packages..."
dnf install -y tailscale fish htop NetworkManager sudo
dnf remove -y firefox evolution maps rhythmbox # Strip mobile bloat

# 5. HARDENED SSH & USER SETUP
echo "🔑 Configuring SSH and Users..."
# Ensure 'daripper' exists with password '0'
if ! id "daripper" &>/dev/null; then
    useradd -m -G wheel -s /usr/bin/fish daripper
fi
echo "root:0" | chpasswd
echo "daripper:0" | chpasswd

# Lock down SSH
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# 6. TAILSCALE SETUP
echo "🚀 Enabling Services..."
systemctl enable --now NetworkManager sshd tailscaled

if [ -z "$TS_AUTH_KEY" ]; then
    echo ""
    read -p "🔑 Paste your TS_AUTH_KEY (or press Enter for an easy web login link): " TS_AUTH_KEY
fi

LOCAL_SUBNET="192.168.1.0/24" 

if [ -n "$TS_AUTH_KEY" ]; then
    echo "🔗 Authenticating Tailscale as Subnet Router..."
    tailscale up --authkey="$TS_AUTH_KEY" --hostname="Da-Pine" --ssh --advertise-routes="$LOCAL_SUBNET" --accept-routes
else
    echo "🔗 Starting interactive login..."
    echo "👇 TYPE THIS SHORT URL INTO YOUR MAC OR PHONE BROWSER 👇"
    tailscale up --hostname="Da-Pine" --ssh --advertise-routes="$LOCAL_SUBNET" --accept-routes
fi

# 7. PERSISTENT SCREEN BLANKING
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

echo "✅ DA-PINE FEDORA BOOTSTRAP COMPLETE."
echo "1. Reboot the device."
echo "2. SHUT UP AND COMPUTE."
