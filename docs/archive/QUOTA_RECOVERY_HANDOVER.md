# 🛡️ AURA: QUOTA RECOVERY & ARCHITECTURAL HANDOVER

**Status:** Full Strategic Roadmap Phase 3 Complete.
**Objective:** Provide a surgical, step-by-step state report to ensure project continuity if AI quota expires.

---

## 🏛️ 1. THE ARCHITECTURE (HUB-AND-SPOKE)
Aura is a unified monorepo.
- **Root:** Python Engine, Go CLI, and Logic Hub configurations.
- **`mobile/`:** Android Satellite (Samsung/Pixel flavors).
- **Network:** All spokes phone home to the **DA-HP Logic Hub** via Tailscale.

---

## ⚙️ 2. THE LOGIC HUB (DA-HP)
**Hardware:** HP EliteDesk (i7-4790S), 16GB RAM, Arch Linux (CachyOS kernel).
- **Bootstrap Script:** `da-hp-bootstrap.sh` (Configures performance governors, Huge Pages, and Ollama).
- **Core Models:**
  - `aura-qwen:latest` (GEMA / Daily Ops)
  - `aura-deepseek:latest` (Thinking / Debugging)
  - `aura-architect:latest` (16B / Repo Mapping)
- **Autonomous Daemon:** `python/aura_daemon.py`. Wakes every 6 hours to graph the repo and audit security. Installed as a systemd service.
- **Resilience:** Auto-sleep after 120m idle. Wake-on-LAN (WoL) enabled.

---

## 📱 3. THE MOBILE SPOKES (ANDROID)
Divided into two hardware tiers in `mobile/android`:

### A. Samsung Build (Standard)
- Pure communication satellite. No local system manipulation.
- Focus: Biometric security and high-speed chat.

### B. Pixel Build (God-Mode)
- **Shizuku/Rish:** Elevated ADB permissions.
- **Termux:** Linux environment for local tool execution.
- **Tooling:** Uses `shizuku_command` and `termux_command` in `engine.py`.
- **MCP Integration:** Connects to `android-shizuku-mcp` on `localhost:8080` for persistent shell access.

---

## ⚡ 4. RECENT STRATEGIC IMPLEMENTATIONS

### 1. The PinePhone Relay (WoL Fix)
- **File:** `PINEPHONE_SUBNET_ROUTER_NOTE.md`
- **Logic:** PinePhone acts as a Tailscale Subnet Router to relay Layer 2 WoL broadcasts to the sleeping DA-HP.

### 2. Advanced Haptic Telemetry
- **File:** `mobile/android/app/src/main/java/com/aura/app/HapticHelper.kt`
- **API:** Uses `VibrationEffect.Composition`.
- **Patterns:** State Awakening (Thud+Spin), Biometric Reject (Double-Drop), Disconnect (Snap).

### 3. Dynamic Vision Routing
- **File:** `python/aura_core/engine.py`
- **Logic:** Intercepts prompt regex for `.jpg/.png`. Auto-routes to `moondream:latest`.

---

## 🚀 5. IMMEDIATE NEXT STEPS (FOR THE NEXT AGENT)

1. **Configure PinePhone:** Follow `PINEPHONE_SUBNET_ROUTER_NOTE.md` on the physical device.
2. **Android MCP Setup:** Install and start the `android-shizuku-mcp` server within Termux on the Pixel.
3. **Windows Lite Build:** 
   - Implement `qframelesswindow` in `python/aura/ui/window.py` for the Windows client.
   - Configure DirectML backend for local fallback.
4. **Haptic Finalization:** Map more engine events to the `HapticHelper` rhythms in `MainActivity.kt`.

---
*Aura // Living Hub. SHUT UP AND COMPUTE.*
