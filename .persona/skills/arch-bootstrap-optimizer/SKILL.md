# Skill: arch-bootstrap-optimizer

This skill provides the logic and templates for reviewing and optimizing Arch Linux bootstrap scripts.

## Workflow

### 1. Verification
- Ensure `base`, `base-devel`, and a kernel are present.
- Verify `linux-firmware` and microcode (intel/amd) are included.
- Check for modern bootloader implementation (systemd-boot preferred).

### 2. Optimization
- Inject `PARTUUID` detection for boot entries.
- Optimize `fstab` generation.
- Ensure services like `NetworkManager` and `sshd` are enabled.

### 3. Hardware-Specific Tuning
- Detect HP-specific needs (e.g., blacklisting `hp-wmi`).
- Apply CPU governor settings (performance mode for AI workloads).

## Implementation Rules
- Use `arch-chroot` for all internal configurations.
- Ensure `set -e` is used for fail-fast behavior.
- Use `genfstab -U` for UUID-based mounting.
