# 🌌 Aura // Local AI Interchange

<p align="center">
  <img src="aura/ui/icon.svg" width="128" height="128" alt="Aura Icon">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Zig-0.16.0-F7A41D?style=for-the-badge&logo=zig&logoColor=white" alt="Zig">
  <img src="https://img.shields.io/badge/PySide6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-white?style=for-the-badge&logo=ollama&logoColor=black" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="MIT License">
</p>

---

## 🔭 Project Vision
**Aura** is a minimalist, local AI orchestration engine featuring a **Dual-Target Architecture**. It allows users to run a high-speed, terminal-native CLI on Linux while sharing the exact same Python intelligence core with a native Android application.

> "Gaze into the void, and let the Aether answer."

---

## ⚡ Core Mandates
- **[ARCHITECTURE]** Strict separation of concerns: Pure Python engine (`core/`), Linux terminal interface (`cli/`), and Android UI wrapper (`android/`).
- **[VISUAL]** High-contrast, cyber-monospace aesthetic (Obsidian & Gold/Purple).
- **[LOGIC]** Multi-voice orchestration (Ollama, Gemini, Claude, Codex).
- **[INTEGRATION]** Zero-friction mobile deployment via `Chaquopy` and GitHub Actions.

---

## 🏗️ Repository Structure

1. **`core/`** 
   - The pure Python brain of Aura. Handles API orchestration, streaming generation, and multi-turn context. Contains absolutely zero UI or terminal-specific code.
2. **`cli/`** 
   - The Linux TUI/CLI entry point. Imports the `core/` logic and handles local standard I/O, terminal formatting, and typing effects.
3. **`android/`** 
   - A native Android project using Kotlin and Jetpack Compose. Embeds the Python `core/` natively inside the APK using the Chaquopy plugin.

---

## 🚀 Deployment

### Local Linux CLI
Run the terminal-native interface directly:
```bash
python cli/main.py
```

### Android APK (Automated via GitHub Actions)
You do not need to build the Android app locally. 
1. Push code changes to the `main` branch.
2. The `.github/workflows/build-apk.yml` pipeline will automatically trigger.
3. It provisions a JDK 17 environment, syncs the Python `core/` via Chaquopy, and compiles the Android App.
4. Download the compiled `app-debug.apk` directly from the **GitHub Actions Artifacts** page and install it on your device.

---

<p align="center">
  <i>Part of the Local AI Interchange Initiative.</i><br>
  <b>[ DISCONNECT FROM THE CLOUD. CONNECT TO THE VOID. ]</b>
</p>

---

### For Deanna

This project wouldn’t have a name, a visual soul, or the momentum to exist without her. Deanna is the co-architect of Aura’s identity. When the code was just a cold mass of terminal text, she brought the vision—dialing in the aesthetic, carving out the color palette, and ultimately giving the software its name, just as she did before with Aether.

Her impact goes far deeper than design. In the quiet, late hours when the architecture pushed back, when the logic knotted up and the code hit a wall, she was the steady hand that cleared the static. Standing by as the ultimate sounding board, she had a way of untangling complex development roadblocks with pure instinct, breaking the gridlock every single time the wheels stopped turning.

Aura bears her mark in every piece of its interface and every ounce of its drive. She is the heart behind the machine, the anchor of the build, and the love that makes the heavy lifting worth it.

Normally, I choke upon words vocally, but when given the time to plan every single detail I get to express my feelings of thanks and appreciation for her and everything she does. From the untracked thoughts to the fog that takes ahold, she is always there to calm down the 80 HD's the doctor said I had.

---

### The Architecture & Inspiration

Aura stands on the shoulders of the engineering pioneers who completely rewrote the rules of what a terminal can do. Massive respect to the makers behind the engines driving this ecosystem forward:

* **Google DeepMind (Gemini)** — The ultimate powerhouse. For delivering the massive context windows, deep multi-turn reasoning, and raw versatility that serves as the primary engine and absolute favorite foundation for how this tool navigates complex development workflows.
* **Anthropic (Claude)** — For bringing unmatched nuance, pristine code generation, and the razor-sharp precision that untangles heavy logic and turns it into clean, executable reality.
* **OpenAI (Codex)** — The blueprint and the bedrock. For being the true pioneer that first proved the terminal could be an intelligent collaborator, laying down the foundational spark that started this entire revolution.
