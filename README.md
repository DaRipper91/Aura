# 🌌 Aura // Dual-Target AI Orchestration

Aura is a high-performance local AI interchange designed for a **Dual-Target Architecture**. It allows you to run a terminal-aesthetic GUI or a native TUI on Linux while sharing the exact same Python intelligence core with a native Android application.

---

## 🏗️ Repository Architecture

1.  **`core/`** 🧠
    - The pure Python brain. Handles multi-turn context tracking, API orchestration (Ollama, Gemini, Claude), and real-time streaming logic.
    - Strictly logic-only. Zero UI/Terminal dependencies.
2.  **`cli/`** ⌨️
    - The Linux TUI/CLI entry point. Consumes the `core/` logic and handles terminal standard I/O and text formatting for localized Linux workflows.
3.  **`aura/`** 🌌
    - The terminal-aesthetic PySide6 GUI (Aura Dashboard). Optimized for high-contrast, cyber-monospace desktop interaction.
4.  **`android/`** 📱
    - A native Android project using Kotlin and Jetpack Compose. Embeds the Python `core/` natively via the **Chaquopy** plugin for on-device orchestration.

---

## 🚀 Deployment

### 1. Linux GUI (Desktop)
Run the minimalist PySide6 dashboard:
```bash
python main.py
```

### 2. Linux TUI (CLI)
Run the direct terminal interface:
```bash
python cli/main.py
```

### 3. Android APK (Mobile)
You do not need to build the APK locally. 
- **CI/CD:** Every push to the `main` branch triggers the `.github/workflows/build-apk.yml` workflow.
- **Artifacts:** Once the build finishes, download the `aura-debug-apk` from the GitHub Actions run and install it directly on your Android device.

---

## 🛠️ Tech Stack & Mandates
- **Intelligence Core:** Python 3.12+ (AuraEngine)
- **Local Runtime:** Ollama API
- **Desktop UI:** PySide6 (Fusion Theme)
- **Mobile UI:** Jetpack Compose + Kotlin
- **Mobile Runtime:** Chaquopy (Embedded Python 3.11)
- **Engine Core:** **Bolt** (High-performance streaming engine)

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
