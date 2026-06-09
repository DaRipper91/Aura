iso_name="aura-logic-hub"
iso_label="AURA_LOGIC"
iso_publisher="Aura // Gema"
iso_application="Headless AI Orchestrator"
iso_version="1.0"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito' 'uefi-ia32.grub.esp' 'uefi-x64.grub.esp' 'uefi-ia32.grub.eltorito' 'uefi-x64.grub.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_permissions=(
  [etc/shadow]="0:0:400"
  [root]="0:0:750"
  [usr/local/bin/aura-init.sh]="0:0:755"
)
