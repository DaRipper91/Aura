#!/bin/sh
# 🌲 DA-PINE // SUB-ROUTER BOOTSTRAP SCRIPT (postmarketOS / Alpine Linux)
# Target: PinePhone (Original/Pro) - postmarketOS Console
# Role: Layer 2 Wake-on-LAN Relay & Tailscale Subnet Router

set -e
trap 'echo "❌ ERROR: Bootstrap failed at line $LINENO"' ERR

echo "🌲 INITIALIZING DA-PINE BOOTSTRAP (Alpine) // SHUT UP AND COMPUTE."

# 1. HARDWARE OPTIMIZATION (Power & Heat Reduction)
echo "🔋 Disabling Mobile Hardware..."

# Disable Cellular Modem (eg25-manager) on Alpine (OpenRC)
if rc-service eg25-manager status 2>/dev/null | grep -q "started"; then
    rc-service eg25-manager stop
    rc-update del eg25-manager default
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
# Alpine uses apk instead of pacman
apk update
apk add tailscale fish openssh htop networkmanager sudo starship curl

# 4. HARDENED SSH & USER SETUP
echo "🔑 Configuring SSH and Users..."
# pmOS default user is 'user', we'll set up 'daripper'
if ! id "daripper" >/dev/null 2>&1; then
    adduser -D -s /usr/bin/fish daripper
    addgroup daripper wheel
fi

# Set requested passwords for seamless sudo
echo "root:0" | chpasswd
echo "daripper:0" | chpasswd

# Lock down the default 'user' account if it exists
if id "user" >/dev/null 2>&1; then
    echo "user:$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)" | chpasswd
fi

# Lock down SSH
sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# Sudoers
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel

# 5. STARSHIP & FISH OPTIMIZATION
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

# 6. TAILSCALE SETUP
echo "🚀 Enabling Services..."
rc-update add networkmanager default
rc-update add sshd default
rc-update add tailscale default
rc-service tailscale start

if [ -z "$TS_AUTH_KEY" ]; then
    echo ""
    echo "🔑 Paste your TS_AUTH_KEY (or press Enter for an easy web login link): "
    read TS_AUTH_KEY
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
cat <<EOF > /etc/local.d/pinephone-screen-off.start
#!/bin/sh
echo 0 > /sys/class/backlight/backlight/brightness || true
EOF
chmod +x /etc/local.d/pinephone-screen-off.start
rc-update add local default

echo "✅ DA-PINE BOOTSTRAP COMPLETE."
echo "1. Reboot the device."
echo "2. SHUT UP AND COMPUTE."
