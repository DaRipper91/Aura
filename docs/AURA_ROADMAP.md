# AURA ECOSYSTEM: MASTER ROADMAP

## PHASE 1: INFRASTRUCTURE & RELIABILITY (Foundation)
- [x] **Da-HP: "Always Hot" Pre-Loader:** systemd service to preload `aura-qwen` and `aura-architect` into Huge Pages on boot.
- [x] **Da-Pine: Battery Preservation:** Sysfs script to clamp charging between 40%-60% to prevent lithium-ion degradation.
- [x] **Da-Pine: Autonomous Resurrection:** Go/Python daemon to ping Da-HP and broadcast Wake-on-LAN automatically if the Tailnet connection drops.

## PHASE 2: UI/UX & IMMERSION (The Spoke)
- [x] **Aura Desktop: Reactive Glitch Aesthetic:** Bind `trigger_glitch()` to actual system events (tool failures, high latency, context clears).
- [x] **Aura Desktop: Continuous Vision ("Watchful Eye"):** Background thread taking rolling screenshots, auto-attaching to queries routed to `moondream`.

## PHASE 3: DEEP CAPABILITIES (The Sandbox & Brain)
- [x] **Da-HP: Isolated Execution Sandbox:** Headless Docker jail on the Hub for safe remote tool execution (`run_shell_command`).
- [x] **Da-HP: Persistent RAG (Long-Term Memory):** SQLite-based keyword indexing on the Hub for instant context retrieval via `long_term_memory` tool.

## PHASE 4: ADVANCED HARDWARE INTEGRATION (The Edges)
- [x] **Da-Pine: Cellular Telemetry Bridge:** ModemManager integration to pipe SMS/2FA via `check_cellular` tool.
- [x] **Aura Desktop: Local Audio Pipeline:** `spd-say` integration for local, low-latency voice interaction via `voice_synthesis` tool.

## PHASE 5: MOBILE SATELLITE ASCENSION (The Physical Key)
- [x] **Aura APK: Biometric Tool Gating:** `BiometricPrompt` integration to authorize risky Hub commands via fingerprint.
- [x] **Aura APK: UI Parity (Ghost Log):** Ported the Telemetry feed and status HUD to the Compose UI.
- [x] **Aura APK: Seamless Edge Handover:** Automatic Phi-3 failover mechanism for high-latency cellular scenarios.
- [ ] **Aura APK: System Telemetry Bridge:** Pixel 10 Pro sensor data (GPS/Accel) available as tools for the Hub Agent.

---
**STATUS: PHASE 5.2_DEPLOYED // EDGE_FAILOVER_READY**
