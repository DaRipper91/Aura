#!/bin/bash
# DA-HP // ISO BUILD HELPER (Run on Fedora)

echo "🛠️ Building DA-HP Custom Arch ISO via Podman..."

# Build the container
podman build -t aura-iso-builder ./DA-HP-ISO

# Create output directory
mkdir -p ./DA-HP-ISO/output

# Run the build (requires --privileged for loop device mounting inside archiso)
podman run --privileged \
    -v $(pwd)/DA-HP-ISO/output:/output \
    aura-iso-builder

echo "✅ ISO build attempt finished. Check DA-HP-ISO/output/"
