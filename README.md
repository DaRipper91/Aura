# 🌌 AURA // Local AI Interchange

Aura is a high-performance, autonomous agent environment designed as a unified **Hub-and-Spoke** system for local intelligence. It provides a minimalist, terminal-aesthetic interface focused on high-speed response, surgical execution, and total operational sovereignty.

---

## 🏗️ THE ARCHITECTURE: HUB-AND-SPOKE

Aura decouples high-performance AI from cloud dependencies by utilizing a dedicated, performance-tuned local server (The Hub) to serve multiple client devices (The Spokes).

### 🏛️ 1. The Logic Hub (DA-HP)
- **Role:** The "Engine Room". A dedicated, headless Arch Linux server (HP EliteDesk).
- **Network:** Secure orchestration via **Tailscale**.
- **Engine:** Ollama optimized with **Huge Pages (1024)** and AVX2 performance governors.
- **Autonomous Daemon:** Background `aura_daemon.py` service that graphs the repo, audits security, and reviews PRs using the 16B Architect model while the user is away.
- **Resilience:** Auto-sleep (120m idle) with remote **Wake-on-LAN** relay via PinePhone.

### 📱 2. The Mobile Satellite (Android)
- **Pixel Build (God-Mode):** Advanced developer tier. Integrates **Shizuku**, **Rish**, and **Termux** to execute elevated ADB commands and on-device shell scripts.
- **Samsung Build (Standard):** Focused, high-speed chat interface with biometric gating and haptic telemetry.
- **Haptic Telemetry:** Non-verbal feedback rhythms using `VibrationEffect.Composition` for model states and system events.

### 💻 3. The Desktop Spoke (Linux/Windows)
- **Role:** The primary workstation "Command Deck".
- **GUI:** Cyber-Monospace aesthetic built with **PySide6**.
- **Vision Routing:** Dynamic engine logic that auto-switches to `moondream` for image-based prompts.

---

## 🧠 THE POWER COUPLE: DUAL-MODEL ARCHITECTURE

The ecosystem is locked to two core intelligence tiers, eliminating legacy bloat and 1.5B "slop":

1. **Aura Master (Qwen 2.5 Coder 7B):** The daily driver for high-speed surgical coding and execution.
2. **Aura Architect (DeepSeek Coder V2 16B):** The structural brain for deep reasoning, monorepo mapping, and background auditing.

---

## 🛡️ CONSTITUTIONAL MANDATES

Every agent (BOLT, SENTINEL, PALETTE) and every line of code in this repo follows these rules:

- **Identity:** "Shut Up and Compute." Zero conversational filler, high-density technical output.
- **Bolt (Performance):** Minimal latency, RAM/VRAM optimization, and non-blocking stream rendering.
- **Sentinel (Security):** Zero-trust dependency management and mandatory biometric gating for remote tool execution.
- **Palette (Aesthetic):** Obsidian / Gold / Purple colorway. High-contrast, keyboard-first terminal feel.

---

## 🚀 GETTING STARTED

1. **Bootstrap the Hub:** Run `da-hp-bootstrap.sh` on your server.
2. **Connect Spokes:** Open Aura (Desktop or APK), input the Hub's Tailscale IP, and begin.

--
*Aura // Living Hub. MALICIOUS COMPETENCE.*
