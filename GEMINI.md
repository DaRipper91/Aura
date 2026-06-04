# Aura: Local AI Interchange

Aura is a minimalist, terminal-aesthetic GUI for interacting with local LLMs (Phi, Gemma, Qwen). It focuses on high-speed response, low visual noise, and a "living terminal" feel similar to `gemini-cli`.

## 🌌 Project Vision
To provide a focused, aesthetically-pleasing interface for local models that feels like a natural extension of the developer's terminal, rather than a heavy web application.

---

## 🏗️ Architectural Mandates
- **Language:** Python 3.12+ (Strict typing).
- **GUI Framework:** PySide6.
- **Aesthetic:** Minimalist, high-contrast, "cyber-monospace" style.
- **Models:** Integrated with Ollama (Phi, Gemma, Qwen).
- **Core Feature:** Streaming "typewriter" effect with markdown support.

---

## 🛠️ Operational Workflow for Gemini
1. **Keep it Lean:** No heavy dependencies outside of PySide6 and `requests`.
2. **Terminal First:** The UI should prioritize keyboard navigation and look like a high-end CLI.
3. **Model Awareness:** Automatically switch system prompts based on whether Phi (Reasoning), Gemma (Creative), or Qwen (Coding) is selected.
