#!/bin/sh
# 🌲 DA-PINE // PHASE 6.4 UPGRADE SCRIPT
# Role: Restore Modem & Initialize Resilient Node Features

set -e

echo "🌲 UPGRADING DA-PINE TO PHASE 6.4 // EVOLUTION IN PROGRESS."

# 1. MODEM RESURRECTION
echo "📡 Re-enabling EG25 Modem Manager..."
apk add eg25-manager modemmanager
rc-update add eg25-manager default
rc-service eg25-manager start
rc-update add modemmanager default
rc-service modemmanager start

# 2. GPS & LOCATION SERVICES
echo "🛰️ Installing GPS stack..."
apk add gpsd
rc-update add gpsd default

# Configure gpsd to listen to the Quectel EG25 modem
# On PinePhone, the GPS NMEA port is usually /dev/ttyUSB1
sed -i 's/GPSD_OPTIONS=""/GPSD_OPTIONS="\/dev/ttyUSB1"/' /etc/conf.d/gpsd
rc-service gpsd start

# 3. NETWORK FAILOVER TOOLS
echo "🔄 Installing routing tools..."
apk add iproute2 iptables

# 4. AURA MESH SCRIPTS
echo "🧠 Deploying node-level tools..."
mkdir -p /usr/local/bin/aura-tools

# GPS Anchor Tool
cat <<EOF > /usr/local/bin/aura-tools/get-location.sh
#!/bin/sh
# Fetches raw GPS NMEA data from the modem
mmcli -m any --location-status
mmcli -m any --location-get
EOF
chmod +x /usr/local/bin/aura-tools/get-location.sh

# SMS Vault Tool (Draft)
cat <<EOF > /usr/local/bin/aura-tools/read-sms-secure.sh
#!/bin/sh
# Gated by biometric signature (placeholder logic)
mmcli -m any --messaging-list-sms
EOF
chmod +x /usr/local/bin/aura-tools/read-sms-secure.sh

echo "✅ DA-PINE PHASE 6.4 UPGRADE STAGED."
echo "Note: Run this script on Da-Pine once physical connectivity is restored."
