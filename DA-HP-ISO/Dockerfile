# DA-HP // ARCH ISO BUILDER
FROM archlinux:latest

RUN pacman -Sy --noconfirm archiso libisoburn mtools squashfs-tools

WORKDIR /build
COPY . /build/profile

# Command to build the ISO
# Note: Must be run with --privileged or equivalent in Podman/Docker
CMD ["mkarchiso", "-v", "-w", "/tmp/archiso-tmp", "-o", "/output", "/build/profile"]
