# 🌌 AURA: DEEP RESEARCH DOSSIER

**Target Audience:** Gemini Advanced (Deep Research / gemini.google.com)
**Project Context:** Aura Monorepo (Local AI Interchange)
**Goal:** Analyze this dossier to brainstorm next-generation features, architectural improvements, and actionable backlog items for the Aura ecosystem.

---

## 1. PROJECT VISION & PHILOSOPHY
Aura is a high-performance, autonomous agent environment designed as a unified **Hub-and-Spoke** system for local intelligence. 

**The Core Philosophy:**
- **"Malicious Competence":** Zero conversational filler, high-speed execution, direct technical action.
- **"Shut Up and Compute":** The system and its agents must prioritize surgical execution over chatty explanations.
- **"Living Hub":** The system manages its own environment, creates tools, and offloads heavy reasoning to dedicated hardware.

---

## 2. ARCHITECTURE: THE HUB-AND-SPOKE MODEL
The project recently transitioned to a unified monorepo to eliminate fragmented codebases.

### A. 🏛️ The Logic Hub (DA-HP)
- **Role:** The "Engine Room". A dedicated, headless Arch Linux server (HP EliteDesk i7-4790S).
- **Network:** Connected to the ecosystem via Tailscale.
- **Engine:** Ollama optimized with Huge Pages (1024) and AVX2 CPU performance governors.
- **Intelligence Tiers (Pre-configured Modelfiles):**
  1. **Aura Master (GEMA):** `qwen2.5-coder:7b` - The daily surgical execution engine.
  2. **Aura Thinker:** `deepseek-r1:7b` - Deep reasoning for complex debugging.
  3. **Aura Architect:** `deepseek-coder-v2:16b` - Monorepo mapping and structural integrity.
- **Resilience:** Auto-sleep (suspend after 2 hours idle), persistent systemd journaling, and a "Ghost Protocol" (Tailscale SSH enabled on boot) for emergency recovery.

### B. 📱 The Mobile Satellite (Android Spoke)
- **Location:** `mobile/` in the monorepo.
- **Role:** The command deck in your pocket. Phones home to the DA-HP Logic Hub for all heavy lifting.
- **Hardware Tiers:**
  1. **Pixel Build (God-Mode / CLI Tier):** Integrates with **Shizuku**, **Rish**, and **Termux**. The Python engine can execute elevated ADB commands and Termux scripts directly on the device, mimicking a mobile `gemini-cli`.
  2. **Samsung Build (Standard Tier):** A secure, fast chat interface relying purely on the remote hub.
- **Key Features:** Haptic telemetry (syncing vibrations to token streams), Biometric Gating for dangerous tool execution, and Wake-on-LAN (WoL) to wake the sleeping Logic Hub.

### C. 💻 The Desktop Spoke (Linux/Windows/Xbox)
- **Role:** The primary engineering workstation client.
- **Frameworks:** PySide6 (Cyber-Monospace GUI), Python 3.12+ Core, Go (CLI), Rust (Xbox UWP).
- **Integration:** The local Python engine dynamically routes traffic. If the UI specifies a Tailscale IP, it acts as a spoke. If an image is uploaded, it dynamically routes the request to a vision model (`moondream`).

---

## 3. CONSTITUTIONAL MANDATES (THE JULES SUITE)
All autonomous agents acting within the Aura repo are governed by three personas:

1. **⚡ BOLT (Performance):** Optimize for RAM/VRAM, low-latency streaming, and efficiency (e.g., caching hardware detection to prevent UI stutters).
2. **🛡️ SENTINEL (Security):** Zero-trust dependency management. Secure the Tailnet. Use list-based `argv` (never `shell=True`) to prevent command injection.
3. **🎨 PALETTE (UX):** Maintain the "Cyber-Monospace" aesthetic (Obsidian/Gold/Purple). Ensure explicit focus states for keyboard accessibility. High-density technical output.

---

## 4. RECENT MILESTONES (Context for the LLM)
- Unified `Aura` and `Aura-APK` into a single monorepo.
- Bootstrapped DA-HP with automated model pulling and resilience scripts.
- Added `shizuku_command` and `termux_command` to the Python engine's `ToolRegistry` for the Pixel God-Mode build.
- Implemented Dynamic Vision Routing (auto-switching to Moondream for image prompts).
- Integrated a Wake-on-LAN Kotlin stub in the Android app.

---

## 5. CURRENT OPEN BACKLOG
*(Areas currently lacking deep feature definition)*
- **Windows Lite Build:** Needs a frameless "Cyber-Chrome" title bar, DirectML isolation, and multi-threaded stream buffering.
- **Android UI Refinement:** Implementing the Shizuku permission handshakes in Kotlin to match the new Python tools. Haptic feedback patterns for model state transitions.

---

## DEEP RESEARCH INSTRUCTIONS FOR GEMINI:
Based on the comprehensive context above, perform deep research and generate a highly detailed, actionable proposal. Focus on:

1. **"God-Mode" Expansions:** What are 3-5 advanced ways we can utilize the new `shizuku_command` and `termux_command` tools on the Pixel build to make it the ultimate autonomous mobile engineer?
2. **Logic Hub Autonomy:** How can the DA-HP Logic Hub become more proactive? Are there ways it can autonomously manage the monorepo while the user is asleep (e.g., cron-based PR reviews, dependency updating)?
3. **"Living Hub" Aesthetics:** Propose innovative ways to use the Desktop PySide6 GUI or the Android Compose UI to make the AI feel more "alive" without violating the "Shut Up and Compute" low-noise mandate (e.g., telemetry visualization, token-flow UI).
4. **Architectural Weaknesses:** Based on the Hub-and-Spoke and Tailscale setup, identify potential scaling or security bottlenecks (Adversarial Design review).

Provide your findings formatted as a structured markdown report that can be directly ingested into the Aura project planning cycle.