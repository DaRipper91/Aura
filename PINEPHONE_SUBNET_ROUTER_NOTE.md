# 📝 TASK: PinePhone Subnet Router Setup (Wake-on-LAN Relay)

**Context:** The DA-HP Logic Hub is configured to auto-sleep after 2 hours. To wake it remotely via the Aura-APK, we need to bypass Tailscale's Layer 3 limitations. The PinePhone will serve as the Layer 2 Wake-on-LAN relay.

## PREREQUISITES
- PinePhone plugged into power and connected to the home Wi-Fi network.
- PinePhone IP Subnet identified (e.g., `192.168.1.0/24`). Check with `ip a`.

## EXECUTION PROTOCOL (Run on PinePhone)

### 1. Enable IP Forwarding
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

### 2. Install Tailscale (if missing)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### 3. Advertise Subnet Route
*Replace `192.168.1.0/24` with your actual home subnet.*
```bash
sudo tailscale up --advertise-routes=192.168.1.0/24 --accept-routes
```

### 4. Admin Approval
1. Log in to the [Tailscale Admin Console](https://login.tailscale.com/admin/machines).
2. Locate the **PinePhone** device.
3. Select **Edit route settings** (three dots menu).
4. Approve the advertised subnet.

---
*Aura // Living Hub. SHUT UP AND COMPUTE.*