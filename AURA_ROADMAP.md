# 🌌 AURA PROJECT ROADMAP & STATUS REPORT
**Date:** June 10, 2026
**Phase:** Core Infrastructure & Bootstrapping

---

## 🏁 1. Where We Started
The Aura project began with the vision of creating a **Local AI Interchange**—a highly autonomous, low-latency, "Living Hub" for interacting with local LLMs without relying on cloud APIs.

**Initial Architecture:**
*   **The Hub (DA-HP):** An HP EliteDesk running Arch Linux, meant to handle all heavy LLM computation (Ollama, Huge Pages, AVX2 optimization).
*   **The Relay (Da-Pine):** A PinePhone acting as a Wake-on-LAN relay and Tailscale Subnet Router to wake the DA-HP when the user is remote.
*   **The Spokes:** Android (Pixel/Samsung) and Desktop clients acting as the UI.

**Early Challenges:**
*   We struggled with Wi-Fi drivers and bootloader issues (GRUB vs. systemd-boot) on the DA-HP.
*   The automated ISO generation for DA-HP (via GitHub Actions) failed repeatedly due to repository misconfigurations, YAML syntax errors, and missing UEFI bootloader dependencies.
*   The PinePhone (Da-Pine) was running a heavy OS (PostmarketOS with a GUI) making it incredibly slow and RAM-starved.

---

## 🔄 2. What We Changed (The Pivots)

Through ruthless iteration and "Malicious Competence", we stabilized the infrastructure by making several hard pivots:

### The Hub (DA-HP) Pivot
*   **Bootloader:** Migrated completely away from GRUB to a pure, modern **systemd-boot (UEFI)** setup using `PARTUUID` for rock-solid reliability.
*   **Network:** Shifted from interactive `nmcli` to declarative, file-based NetworkManager configuration injected directly into the ISO.
*   **CI/CD:** We stripped down the GitHub Actions workflow, isolated the syntax errors, and successfully automated the ISO build. It now automatically injects the `TS_AUTH_KEY` secret into the bootstrap script for a zero-touch installation.

### The Relay (Da-Pine) Pivot
*   **Arch to Alpine:** We originally planned to run Arch Linux ARM (DanctNIX) on the PinePhone to match the DA-HP. However, DanctNIX mirrors timed out during our chroot pre-bake attempt, proving it was too unstable for critical routing infrastructure.
*   **The Console Switch:** We pivoted to **postmarketOS (Console Only)**. By dropping the GUI and utilizing Alpine Linux's ultra-lightweight `apk` and `OpenRC` ecosystem, the PinePhone will now idle at under 100MB of RAM.
*   **Hardware Assassination:** We updated `da-pine-bootstrap.sh` to permanently kill the PinePhone's cellular modem (`eg25-manager`) and backlight, transforming it into a cold, silent, thermal-efficient router.

---

## 🎯 3. What We Are Trying to Achieve (The Endgame)

The ultimate goal is a **Zero-Friction, Zero-Trust Autonomous Ecosystem**.

### Short-Term Goals (Next Steps)
1.  **Flash Da-Pine:** Download the `postmarketOS` Console image, flash it to the PinePhone, and run our new `da-pine-bootstrap.sh` to lock it in as the Subnet Router.
2.  **Flash DA-HP:** Pull the successfully built ISO from GitHub Releases, install it on the EliteDesk, and let the automated bootstrap script connect it to the Tailnet.

### Medium-Term Goals
1.  **The Android Spoke:** Shift focus to the `./mobile` directory. Ensure the Aura-APK securely connects to the DA-HP over Tailscale and can reliably send the Wake-on-LAN packet to Da-Pine.
2.  **Daemon Orchestration:** Bring `aura_daemon.py` online on the DA-HP so the 16B Architect model can start auditing code and graphing the repo in the background.

### Long-Term Endgame
*   **Total Autonomy:** You should be able to pull out your Android phone anywhere in the world, request a complex coding task, and have the PinePhone instantly wake the HP EliteDesk. The EliteDesk completes the task, commits the code, and goes back to sleep, all while maintaining strict "Cyber-Monospace" aesthetics and zero conversational filler.

--
*Aura // Living Hub. SHUT UP AND COMPUTE.*