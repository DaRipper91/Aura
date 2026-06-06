# 🤖 Jules Agent Backlog // Aura

This backlog tracks specialized tasks for the Jules Agent Suite (Palette, Sentinel, Bolt).

---

## 📱 APK (Android) // High-Priority

### 1. 🎨 Palette // [APK] Haptic Context Feedback
- **Description:** Implement nuanced haptic patterns for Standalone (SW) mode extraction and model state transitions.
- **Goal:** Use `view.performHapticFeedback` to provide subtle vibration cues when the engine "wakes up" or finishes a model pull.
- **Domain:** UX & Aesthetics.

### 2. 🛡️ Sentinel // [APK] Model Integrity Guard
- **Description:** Create a SHA-256 verification step before initializing MediaPipe.
- **Goal:** Confirm the 1.5GB `QWEN_1.5B.bin` extracted from assets matches the expected hash to prevent corrupted or malicious weight loads.
- **Domain:** Security & Integrity.

### 3. ⚡ Bolt // [APK] MediaPipe Memory Pruning
- **Description:** Optimize the `LocalInferenceEngine` for background lifecycle.
- **Goal:** Aggressively clear the MediaPipe context and free up VRAM/RAM when the app is backgrounded or switched to Remote (RE) mode.
- **Domain:** Performance & Optimization.

---

## 💻 Windows (Lite) // High-Priority

### 1. 🎨 Palette // [Windows] Frameless Cyber-Chrome
- **Description:** Implement a custom frameless window with a dark, high-contrast title bar and neon-glow borders.
- **Goal:** Replace the standard Windows "Fusion" title bar with a terminal-native look that matches the "Cyber-Monospace" aesthetic.
- **Domain:** UX & Aesthetics.

### 2. 🛡️ Sentinel // [Windows] DirectML Isolation
- **Description:** Secure the planned DirectML backend implementation.
- **Goal:** Ensure the engine only communicates with authenticated DirectML drivers and doesn't leak model weights into accessible system memory regions.
- **Domain:** Security & Integrity.

### 3. ⚡ Bolt // [Windows] Multi-Threaded Stream Buffering
- **Description:** Refactor the streaming logic in `engine.py` for high-load scenarios.
- **Goal:** Use a non-blocking queue for the Windows Lite build to ensure the "typewriter" effect remains fluid (60fps) even when the CPU is under 100% load during local inference.
- **Domain:** Performance & Optimization.
