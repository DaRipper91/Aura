# 🌌 Aura // Local AI Interchange

<p align="center">
  <img src="aura/ui/icon.svg" width="128" height="128" alt="Aura Icon">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-white?style=for-the-badge&logo=ollama&logoColor=black" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="MIT License">
</p>

---

## 🔭 Project Vision
**Aura** is a minimalist, terminal-aesthetic GUI designed for high-speed interaction with local Large Language Models (LLMs) via Ollama. It prioritizes low visual noise and a "living terminal" feel, serving as a focused bridge between the developer's command line and local intelligence.

> "Gaze into the void, and let the Aether answer."

---

## ⚡ Core Mandates
- **[SYSTEM]** Pure Python 3.12+ implementation.
- **[VISUAL]** High-contrast, cyber-monospace aesthetic.
- **[LOGIC]** Multi-voice orchestration (Phi, Gemma, Qwen).
- **[ENGINE]** Real-time streaming typewriter effects with Markdown rendering.

---

## 🛠️ Tech Stack
- **GUI Engine:** `PySide6` (Qt for Python)
- **Model Orchestration:** `Ollama` API
- **Processing:** `requests` & `json` (Streaming chunks)
- **Formatting:** `markdown-it-py` (CommonMark compliant)

---

## ⌨️ Command Interface
Aura utilizes a "Command First" approach for model orchestration.

| Command | Voice | Specialization |
| :--- | :--- | :--- |
| `/phi` | **Phi-3 Mini** | Logic & Structured Reasoning |
| `/gemma` | **Gemma 2 2B** | Creative & Expressive Prose |
| `/qwen` | **Qwen 2.5 Coder** | Expert Software Engineering |

---

## 🚀 Deployment

### 1. Prerequisites
Ensure you have **Ollama** installed and the following models pulled:
```bash
ollama pull phi3:mini
ollama pull gemma2:2b
ollama pull qwen2.5-coder:1.5b
```

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/Aura.git
cd Aura

# Install dependencies
pip install PySide6 requests markdown-it-py
```

### 3. Execution
```bash
python main.py
```

---

## 🌌 The Aesthetic
Aura is designed to feel "alive."
- **Status Bar:** Real-time feedback of the active digital voice.
- **Typography:** Optimized for `Cascadia Code` or your system's best monospace.
- **Interaction:** Pulsing typewriter effect for streamed tokens.

---

<p align="center">
  <i>Part of the Local AI Interchange Initiative.</i><br>
  <b>[ DISCONNECT FROM THE CLOUD. CONNECT TO THE VOID. ]</b>
</p>
