# Phase 6 Architecture: The Autonomous Mesh

## Objective
Transition Aura from a "Tool Suite" to a "Unified Organism" where the Hub Agent manages the fleet autonomously.

## 6.1: The Collective Mind (Orchestration)
- **Concept:** Hub as the "Brain", all other nodes as "Limbs".
- **Mechanism:** `dispatch_task(node_id, tool, args)` tool.
- **Data Flow:** Hub receives a goal -> Identifies which device has the best capability (e.g., Pine for SMS, Pixel for GPS, Asahi for Desktop interaction) -> Dispatches sub-tasks.

## 6.2: The Sentinel Heart (Proactive Maintenance)
- **Concept:** Continuous Health Monitoring.
- **Logic:** Hub queries all nodes for thermal/battery state every 5 minutes.
- **Action:** If Pixel battery < 20%, Hub Agent restricts Vision tasks. If Da-HP thermals spike, Hub shifts inference to local Phi-3 on the Spoke.

## 6.3: The Voice of Aura (Whisper 2.0)
- **Concept:** Conversational Ubiquity.
- **Implementation:** Integrated `whisper-tflite` (Small/Base) on Android and Asahi.
- **Trigger:** "Wake Aura" local keyword detection -> Stream audio to Hub for processing.

## Security (SENTINEL)
All cross-node dispatches MUST be signed by the Biometric Key if they involve `RISKY` operations on the target node.
