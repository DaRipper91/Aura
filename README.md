# 🌌 AURA // Local AI Interchange

Aura is a high-performance, autonomous agent environment designed as a unified **Hub-and-Spoke** system for local intelligence. It provides a minimalist, terminal-aesthetic interface focused on high-speed response, low visual noise, and distributed logic offloading.

## 🏗️ MONOREPO ARCHITECTURE

Aura is organized as a unified monorepo for seamless "Logic Hub" and "Satellite" orchestration:

- **🏛️ CORE & HUB (`./`):** The engine room. Python-based agentic core, Go-native CLI, and the **DA-HP Logic Hub** configuration for heavy-duty inference.
- **📱 MOBILE SATELLITE (`./mobile/`):** The spoke interface. Kotlin/Android native application for remote orchestration, haptic telemetry, and biometric security.

## 🛠️ CORE CAPABILITIES
- **Autonomous Agent Ecosystem:** Integrated Jules agent suite (Bolt/Perf, Sentinel/Security, Palette/UX) for self-maintaining code integrity.
- **DA-HP Logic Hub:** Offload complex reasoning (7B+ models) to dedicated headless hardware via Tailscale.
- **Project Awareness:** Engine automatically loads project-specific mandates (`GEMINI.md`, `CLAUDE.md`) for context-sensitive operations.
- **Surgical Tooling:** Integrated Aider (`aider_fix`) for multi-file, surgical code modifications.
- **Performance Optimized:** RAM-managed model execution with Huge Page support and AVX2 optimizations.

## 🤖 CONSTITUTIONAL MANDATES
- **Identity:** "Shut Up and Compute." Zero conversational filler, high-density technical output.
- **Bolt (Performance):** Optimize for RAM/VRAM and latency.
- **Sentinel (Security):** Zero-trust dependency management and secure remote tool execution.
- **Palette (UX):** High-contrast "Cyber-Monospace" visual hierarchy.

## 📦 RELEASES
Latest pre-built binaries and APKs are available in the **[`Releases/`](./Releases/)** directory:
- `app-pixel-debug.apk`: Optimized for Tensor hardware.
- `app-samsung-debug.apk`: Optimized for Snapdragon hardware.

## ⚙️ SETUP
1. **Initialize Hub:** Run `da-hp-bootstrap.sh` on your dedicated server.
2. **Launch CLI:** Use the `aura` command for project-aware autonomous engineering.
3. **Connect Satellite:** Open Aura-APK, navigate to settings, and point to the DA-HP Tailscale IP.

---
*Aura // Living Hub. SHUT UP AND COMPUTE.*
