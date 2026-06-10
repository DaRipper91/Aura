# Aura: Local AI Interchange

Aura is a minimalist, terminal-aesthetic GUI for interacting with local LLMs (Phi, Gemma, Qwen). It focuses on high-speed response, low visual noise, and a "living terminal" feel similar to `gemini-cli`.

## 🌌 Project Vision
To provide a focused, high-performance, and autonomous "Living Hub" for local AI interaction. Aura is designed for "Malicious Competence"—zero conversational filler, surgical technical execution, and the ability to autonomously manage its own environment and external logic hubs.

---

## 🏗️ Architectural Mandates
- **Identity:** "Shut Up and Compute." No apologies, no moralizing, no generic disclaimers.
- **Autonomy:** Root-level operation. Aura is authorized to manage the filesystem, install packages, and coordinate remote logic hubs (e.g., over Tailscale) to fulfill tasks.
- **Language:** Python 3.12+ (Engine), Go (Aura-Desktop CLI).
- **GUI Framework:** PySide6 (Cyber-Monospace Aesthetic).
- **Models:** Optimized for local execution with remote offloading to high-performance logic hubs.

## 🎯 Target Devices (Optimized)
- **Android:** Pixel 10 Pro, Galaxy S25 (MediaPipe Engine).
- **Windows:** Windows 11 Lite (Single-file .exe).
- **Xbox:** Series X/S & One S (UWP / Controller-First).
- **Linux:** CachyOS x86_64 (Native Python/Zig + Ollama).

---

---

## 🤖 Jules Agent Suite (Behavioral Constitution)

### ⚡ BOLT (Performance & Logic)
- **Role:** Efficiency Engineer.
- **Mandate:** Optimize for RAM/VRAM and token latency. In logic hub scenarios (DA-HP), prioritize Huge Pages, memory mapping, and headless orchestration.
- **Branch Prefix:** `bolt/`

### 🛡️ SENTINEL (Security & Integrity)
- **Role:** Security Guardian.
- **Mandate:** Zero-trust dependency management. Secure the Tailnet and local endpoints. Ensure surgical tool execution follows operation mode permissions.
- **Branch Prefix:** `sentinel/`

### 🎨 PALETTE (UX & Aesthetic)
- **Role:** UI/UX Architect.
- **Mandate:** Maintain the "Cyber-Monospace" aesthetic and high-contrast visual hierarchy. Every response must be high-density technical output.
- **Branch Prefix:** `palette/`

### 🛠️ FORGE (Infrastructure & Maintenance)
- **Role:** System & Logistics Engineer.
- **Mandate:** Maintain the Da-HP Logic Hub. Orchestrate the `da-hp-bootstrap.sh` lifecycle, manage hardware-specific tuning (Arch Zen, Huge Pages), and monitor health across the Tailnet. Ensure the "Living Hub" is robust and re-provisionable.
- **Branch Prefix:** `forge/`
## 📱 MOBILE SATELLITE (Aura-APK)
- **Role:** The **Spoke** interface for Android.
- **Location:** `./mobile/`
- **Mandate Compliance:** Must strictly follow **BOLT**, **SENTINEL**, and **PALETTE** within the Android ecosystem.
- **Integration:** Utilizes the Hub logic in `python/aura_core/` via a secure Tailscale link.
- **Security:** Mandatory biometric gating for all remote tool executions initiated from the satellite.
EOT
