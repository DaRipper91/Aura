#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="aura-logic-hub"
iso_label="AURA_LOGIC"
iso_publisher="Aura // Gema"
iso_application="Headless AI Orchestrator"
iso_version="1.0"
install_dir="arch"
buildmodes=('iso')
# Pure UEFI / systemd-boot
bootmodes=(
    'uefi-x64.systemd-boot.esp'
    'uefi-x64.systemd-boot.eltorito'
)
arch="x86_64"
pacman_conf="pacman.conf"

file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/usr/local/bin/aura-init.sh"]="0:0:755"
  ["/usr/local/bin/da-hp-bootstrap.sh"]="0:0:755"
)
