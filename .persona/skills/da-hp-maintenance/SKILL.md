# Skill: da-hp-maintenance

Expertise in the ongoing maintenance and optimization of the Aura Da-HP Logic Hub (HP EliteDesk 800 G1).

## Workflow

### 1. Daily Health Audit
- **hugepages:** Verify `vm.nr_hugepages = 1024` or higher.
- **kernel:** Ensure `linux-zen` is the active kernel (`uname -r`).
- **governor:** Confirm `performance` governor is active for all cores.
- **services:** Check status of `ollama.service`, `tailscaled.service`, and `sshd.service`.

### 2. System Updates
- Use `checkupdates` (if available) or `pacman -Sy` to identify pending core updates.
- Monitor `intel-ucode` updates for security.
- Verify `linux-zen-headers` sync with the active kernel.

### 3. Logic Hub Optimization
- **Ollama:** Check for newly pulled models and verify memory mapping.
- **Huge Pages:** Audit swap usage to ensure LLMs aren't spilling into slow storage.
- **Network:** Monitor Tailscale latency to satellites.

## Implementation Rules
- Never perform a full `pacman -Syu` without verifying kernel stability.
- Always use `systemctl` for service management.
- Prefer `btop` or `htop` for resource monitoring.
- All hardware-level changes must be documented in the local `Da-HP_MODELS.md`.
