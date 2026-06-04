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

---

## 🤖 Jules Agent Suite
Jules is our autonomous peer collaborator. He operates across three specialized domains to maintain the integrity and polish of Aura.

### 🎨 Palette (UX & Aesthetics)
- **Role:** UI/UX Architect.
- **Mandate:** Ensure the "Cyber-Monospace" aesthetic is never compromised. Focus on accessibility, fluid transitions, and visual hierarchy.
- **Workflow:** Weekly audit of `aura/ui/`.
- **Branch Prefix:** `palette/`

### 🛡️ Sentinel (Security & Integrity)
- **Role:** Security Guardian.
- **Mandate:** Zero-trust dependency management. Scan for leaked secrets, insecure API usage in `requests`, and verify `Ollama` endpoint safety.
- **Workflow:** Nightly vulnerability sweep.
- **Branch Prefix:** `sentinel/`

### ⚡ Bolt (Performance & Optimization)
- **Role:** Efficiency Engineer.
- **Mandate:** Optimize token streaming latency and memory footprint of the PySide6 event loop. Ensure the "typewriter" effect remains smooth.
- **Workflow:** Nightly performance profiling.
- **Branch Prefix:** `bolt/`
