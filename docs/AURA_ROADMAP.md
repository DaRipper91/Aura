# AURA ECOSYSTEM: MASTER ROADMAP

## PHASE 1: INFRASTRUCTURE & RELIABILITY (Foundation)
- [ ] **Da-HP: "Always Hot" Pre-Loader:** systemd service to preload `aura-qwen` and `aura-architect` into Huge Pages on boot.
- [ ] **Da-Pine: Battery Preservation:** Sysfs script to clamp charging between 40%-60% to prevent lithium-ion degradation.
- [ ] **Da-Pine: Autonomous Resurrection:** Go/Python daemon to ping Da-HP and broadcast Wake-on-LAN automatically if the Tailnet connection drops.

## PHASE 2: UI/UX & IMMERSION (The Spoke)
- [ ] **Aura Desktop: Reactive Glitch Aesthetic:** Bind `trigger_glitch()` to actual system events (tool failures, high latency, context clears).
- [ ] **Aura Desktop: Continuous Vision ("Watchful Eye"):** Background thread taking rolling screenshots, auto-attaching to queries routed to `moondream`.

## PHASE 3: DEEP CAPABILITIES (The Sandbox & Brain)
- [ ] **Da-HP: Isolated Execution Sandbox:** Headless Docker/systemd-nspawn jail on the Hub for safe remote tool execution (`run_shell_command`).
- [ ] **Da-HP: Persistent RAG (Long-Term Memory):** ChromaDB/Qdrant integration to index project files and chat logs for instant context retrieval.

## PHASE 4: ADVANCED HARDWARE INTEGRATION (The Edges)
- [ ] **Da-Pine: Cellular Telemetry Bridge:** ModemManager integration to pipe SMS/2FA securely over the Tailnet to the desktop UI.
- [ ] **Aura Desktop: Local Audio Pipeline:** `whisper.cpp` (STT) and `piper` (TTS) integration for local, low-latency voice interaction.
