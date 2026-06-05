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
