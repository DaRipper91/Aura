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
**Aura** is a minimalist, terminal-aesthetic GUI designed for high-speed interaction with local Large Language Models (LLMs) via Ollama. It features a **Zig-based Bolt Engine** for low-latency streaming and a hybrid Python/PySide6 UI for a fluid, "living terminal" experience.

> "Gaze into the void, and let the Aether answer."

---

## ⚡ Core Mandates
- **[SYSTEM]** Hybrid Python 3.12+ (UI) & Zig 0.16.0 (Engine) implementation.
- **[VISUAL]** High-contrast, cyber-monospace aesthetic.
- **[LOGIC]** Multi-voice orchestration (Phi, Gemma, Qwen, DeepSeek).
- **[ENGINE]** **Bolt Core:** Zig-powered real-time streaming with zero-copy JSON parsing.

---

## 🛠️ Tech Stack
- **UI Engine:** `PySide6` (Qt for Python)
- **High-Performance Core:** `Zig 0.16.0` (Ollama Bolt Engine)
- **Model Orchestration:** `Ollama` API
- **Formatting:** `markdown-it-py` (CommonMark compliant)

---

## ⌨️ Command Interface
Aura utilizes a "Command First" approach for model orchestration.

| Command | Voice | Specialization |
| :--- | :--- | :--- |
| `/phi` | **Phi-3 Mini** | Logic & Structured Reasoning |
| `/gemma` | **Gemma 2 2B** | Creative & Expressive Prose |
| `/qwen` | **Qwen 2.5 Coder** | Expert Software Engineering |
| `/deepseek`| **DeepSeek R1** | Reasoning & Step-by-Step Logic |

---

## 🚀 Deployment

### 1. Prerequisites
Ensure you have **Ollama** installed and the following models pulled:
```bash
ollama pull phi3:mini
ollama pull gemma2:2b
ollama pull qwen2.5-coder:1.5b
ollama pull deepseek-r1:8b
```

### 2. Build the Bolt Engine (Zig)
```bash
cd aura/bolt
zig build -Doptimize=ReleaseFast
```

### 3. Install Python UI Dependencies
```bash
# From project root
pip install PySide6 requests markdown-it-py
```

### 4. Execution
```bash
python main.py
```

---

## 🌌 The Aesthetic
Aura is designed to feel "alive."
- **Void Settings:** Real-time control over Temperature, Top\_P, and Context.
- **Dynamic Typography:** Hot-swapping of monospace fonts and sizes.
- **Pulsing Typewriter:** Low-latency token rendering powered by the Zig core.

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
