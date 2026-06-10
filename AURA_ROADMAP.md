# 🌌 AURA PROJECT ROADMAP & STATUS REPORT
**Date:** June 10, 2026
**Phase:** Core Infrastructure & Bootstrapping

---

## 🏁 1. Where We Started
The Aura project began with the vision of creating a **Local AI Interchange**—a highly autonomous, low-latency, "Living Hub" for interacting with local LLMs without relying on cloud APIs.

**Initial Architecture:**
*   **The Hub (DA-HP):** An HP EliteDesk running Arch Linux, meant to handle all heavy LLM computation (Ollama, Huge Pages, AVX2 optimization).
*   **The Relay (Da-Pine):** A PinePhone acting as a Wake-on-LAN relay and Tailscale Subnet Router.
*   **The Spokes:** Android (Pixel/Samsung) and Desktop clients.

---

## 🔄 2. The OS Mandates (The Pivots)

We have finalized the operating system choices for each tier to ensure maximum stability and ecosystem alignment:

### 🏛️ 1. The Logic Hub (DA-HP)
- **OS:** **Arch Linux (x86_64)**
- **Bootloader:** systemd-boot (UEFI) with `PARTUUID`.
- **Reasoning:** Cutting-edge performance, native Ollama support, and total control over the kernel for Huge Pages and AVX2 tuning.
- **Status:** Automated ISO build via GitHub Actions is live.

### 🌲 2. The Relay Router (Da-Pine)
- **OS:** **postmarketOS (Alpine Linux / Console / aarch64)**
- **Init System:** OpenRC.
- **Reasoning:** Extreme minimalism. By stripping the GUI, we keep RAM usage <100MB, ensuring the phone stays cool and responsive as a 24/7 subnet router.
- **Status:** `da-pine-bootstrap.sh` refactored for `apk` and `OpenRC`. Native aarch64 build capability established on host.

### 📱 3. The Mobile Satellite (Android)
- **OS:** **Android 15 (Pixel 10 Pro)**
- **Integration:** Termux / Shizuku / Rish.
- **Reasoning:** High-speed remote orchestration and local "Emergency" inference.

---

## 🎯 3. Next Steps (Active Backlog)

1.  **Da-Pine Deployment:** Flash the postmarketOS Console image and run the bootstrap script to activate the subnet router.
2.  **DA-HP Deployment:** Install the custom Arch ISO on the HP EliteDesk and verify Tailscale connectivity.
3.  **Android Integration:** Finalize the haptic feedback and Shizuku tool execution logic in the `./mobile` folder.
4.  **Autonomous Daemon:** Bring `aura_daemon.py` online on DA-HP for background auditing.

--
*Aura // Living Hub. MALICIOUS COMPETENCE.*
