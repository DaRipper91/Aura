# 🌌 Aura // Standalone AI Helper

Aura is a high-performance local AI interchange designed for **Standalone Mobile Intelligence**. It transforms your phone from a simple chat interface into an autonomous "Helper" using on-device NPU acceleration and advanced system-level orchestration.

---

## 🏗️ The "Standalone" Architecture

Aura v1.0.4+ introduces a **Three-Tier Engine** design to ensure "God Mode" performance across all hardware:

1.  **Tier 1: Pixel-Native (Gemini Nano)** 🧬
    - Leverages Android **AICore** on the Pixel 10 Pro (Tensor G5).
    - Hardware-accelerated, zero-battery-drain inference.
2.  **Tier 2: Aura-Internal (MediaPipe LLM)** 🧠
    - On-device inference using the phone's GPU/NPU.
    - Optimized for **Galaxy S25 (Snapdragon 8 Elite)**.
    - Runs quantized versions of **Qwen**, **Gemma**, and **Phi** natively.
3.  **Tier 3: Advanced Command (Shizuku & Rish)** ⚡
    - Bypasses Android's filesystem blocks using the **Shizuku API**.
    - Allows Aura to perform system-level "Helper" tasks (file management, automation).
    - Integrates with **Termux** for heavy 7B+ orchestration.

---

## 🛠️ Tech Stack & Protocols

- **Logic Core:** Python 3.12+ (Shared across Desktop & Mobile).
- **Mobile Engine:** MediaPipe LLM Inference API (0.10.14).
- **Desktop UI:** PySide6 (Fusion Cyber-Monospace).
- **Mobile UI:** Jetpack Compose + Kotlin.
- **Protocols:**
    - **BOLT:** 30FPS+ neural logic optimization.
    - **SENTINEL:** Symbolic sovereignty and security monitoring.
    - **PALETTE:** Aesthetic consistency designed by Deanna.

---

## 🚀 Deployment

### 1. Standalone APK
- **Auto-Build:** Every push to `main` builds a new master APK via GitHub Actions.
- **Model Download:** On first launch, Aura will "Pull" the required local model (e.g., Qwen 1.5B) directly to your device.
- **Advanced Mode:** Enable Shizuku in Settings to unlock root-level "Helper" capabilities.

### 2. Desktop Dashboard
```bash
python main.py
```
- **Auto-Start:** Aura automatically starts the local Ollama server if it detects it isn't running.

---

## 💜 For Deanna

This project is a visual soul carved out by Deanna. From the "D. Anna" theme in Aether to the "VOID" aesthetic of Aura, she is the architect of the experience. Aura isn't just code; it's a reflection of the love and instinct she brings to every build.

---

### Acknowledgments
* **Google DeepMind** — For the Gemini Nano and MediaPipe bedrock.
* **Samsung & Qualcomm** — For the Snapdragon 8 Elite NPU power.
* **The Shizuku Team** — For the keys to the Android system.

│ Aura — Pure Signal. Standalone Intelligence.
