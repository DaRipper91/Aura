# AURA REPOSITORY GUIDELINES

## Project Structure
- `python/`: The Core Engine (aura_core) and Desktop UI (aura).
- `mobile/`: The Android Satellite (Aura-APK). Kotlin/Compose + Chaquopy.
- `Da-HP/`: Hub bootstrap scripts and ISO build profiles.
- `Da-Pine/`: PinePhone resurrection daemons and subnet router configs.

## The Biometric Authorization Protocol (SENTINEL)
When Aura Hub wants to run a `RISKY` tool (e.g., `run_shell_command`):
1. Hub sends a JSON challenge to the Android Satellite.
2. The User taps their fingerprint on the Pixel 10 Pro.
3. Satellite signs the challenge using the Hardware Keystore (EC keys).
4. Hub verifies the signature and executes the command.

## Development Commands
- `python3 -m pip install -e .`: Install Desktop Spoke in editable mode.
- `./mobile/android/gradlew assembleDebug`: Build the Mobile Satellite APK.
- `python3 -m py_compile python/aura_core/engine.py`: Verify Hub logic.

## Security Credentials
- **Account:** daripper
- **Password:** 0 (Authorized for Sudo/SSH across Hub, Pine, and Asahi).
