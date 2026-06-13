# Phase 6.3: Whisper 2.0 Integration Implementation Plan

## Overview
Replaces the online `RecognizerIntent` with an offline, on-device Whisper TFLite engine to fulfill the BOLT and SENTINEL mandates (efficiency, offline security). Implements an "Always Listening" background service using a rolling audio buffer and a lightweight wake word engine ("Wake Aura") to trigger the heavy TFLite inference only when necessary.

## Scope Definition (CRITICAL)
### In Scope
- Update `AndroidManifest.xml` with `FOREGROUND_SERVICE_MICROPHONE`.
- Add TensorFlow Lite and Porcupine (wake word) dependencies to `build.gradle`.
- Modify `AuraService` to manage an `AudioRecord` rolling buffer.
- Implement `WhisperEngine.kt` for local `.tflite` model execution.
- Update `ChatScreen` UI to show Ghost Log updates for mic status and add an "Always Listening" toggle.
### Out of Scope (DO NOT TOUCH)
- Changes to the Chaquopy Python engine.
- Modifications to the remote Logic Hub (DA-HP) connectivity.
- Training or fine-tuning the Whisper model (we assume the use of a pre-trained `whisper-tiny.en.tflite` placed in `assets/`).

## Current State Analysis
- `mobile/android/app/src/main/java/com/aura/app/MainActivity.kt`: Lines 47-53 rely on `RecognizerIntent.ACTION_RECOGNIZE_SPEECH` which routes audio to Google servers.
- `mobile/android/app/src/main/java/com/aura/app/AuraService.kt`: Currently declared as `specialUse` foreground service (lines 11-19). Lacks microphone integration.
- `mobile/android/app/src/main/AndroidManifest.xml`: Lacks `android.permission.FOREGROUND_SERVICE_MICROPHONE`.
- `mobile/android/app/build.gradle`: Missing TFLite and Wake Word dependencies required for edge inference.

## Implementation Phases

### Phase 1: Dependency & Permission Setup (SENTINEL Mandate)
- **Goal**: Add necessary libraries and secure permissions to allow offline audio recording without data leakage.
- **Steps**:
  1. [ ] **Step 1 (Dependencies):** Modify `mobile/android/app/build.gradle`. Add `implementation 'org.tensorflow:tensorflow-lite:2.14.0'`, `implementation 'org.tensorflow:tensorflow-lite-support:0.4.4'`, and `implementation 'ai.picovoice:porcupine-android:3.0.1'`.
  2. [ ] **Step 2 (Manifest Permissions):** Modify `mobile/android/app/src/main/AndroidManifest.xml`. Add `<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />`.
  3. [ ] **Step 3 (Service Declaration):** Modify `mobile/android/app/src/main/AndroidManifest.xml`. Update the `AuraService` declaration: `android:foregroundServiceType="specialUse|microphone"`.
- **Verification**: Run `./gradlew assembleDebug` in the terminal to ensure dependency resolution and build success.

### Phase 2: WhisperEngine & Wake Word Architecture (BOLT Mandate)
- **Goal**: Build the core TFLite wrapper and a highly efficient rolling buffer for wake-word listening to minimize RAM pressure.
- **Steps**:
  1. [ ] **Step 1 (Engine Class):** Create `mobile/android/app/src/main/java/com/aura/app/WhisperEngine.kt`. Initialize a TFLite `Interpreter` loading `whisper-tiny.en.tflite` from assets. Define `fun transcribe(audioBuffer: FloatArray): String` that processes 16kHz mono audio.
  2. [ ] **Step 2 (Rolling Buffer):** Modify `mobile/android/app/src/main/java/com/aura/app/AuraService.kt`. Initialize `AudioRecord` (16kHz, Mono, PCM_FLOAT or PCM_16BIT). Implement a circular buffer array that holds exactly 5 seconds of audio to prevent OOM.
  3. [ ] **Step 3 (Wake Word Trigger):** Modify `mobile/android/app/src/main/java/com/aura/app/AuraService.kt`. Instantiate `PorcupineManager` listening for "Wake Aura". On detection callback, copy the current 5-second circular buffer, pass it to `WhisperEngine.transcribe()`, and broadcast the result via `Intent` or `LocalBroadcastManager`.
- **Verification**: Write a temporary debug log in `AuraService` and manually verify via logcat that "Wake Aura" is detected and triggers the `transcribe` function without crashing.

### Phase 3: UI Integration & Ghost Log
- **Goal**: Connect the background transcription engine to the Compose UI, replacing the old Google Intent.
- **Steps**:
  1. [ ] **Step 1 (Bridge Registration):** Modify `mobile/android/app/src/main/java/com/aura/app/AuraBridge.kt`. Add an intent receiver or callback mechanism `fun setOnTranscriptionListener(listener: (String) -> Unit)` to capture results from `AuraService`.
  2. [ ] **Step 2 (Settings Toggle):** Modify `mobile/android/app/src/main/java/com/aura/app/MainActivity.kt`. In the `SettingsPanel` composable, add a `ToggleRow("ALWAYS_LISTENING", ...)` mapped to a state variable. When true, bind to `AuraService` and enable the microphone.
  3. [ ] **Step 3 (Ghost Log Updates):** Modify `mobile/android/app/src/main/java/com/aura/app/MainActivity.kt`. In the `ChatScreen` composable, intercept `AuraBridge` status broadcasts to append `"MIC_ACTIVE"`, `"WAKE_WORD: DETECTED"`, and `"WHISPER: INFERENCING..."` to the `ghostLog`. Replace `startSpeechRecognition()` with injecting the transcribed text into `inputText` and auto-submitting.
- **Verification**: Run the app on a physical device. Toggle "ALWAYS_LISTENING", say the wake word, and verify the Ghost Log updates dynamically and the transcribed text appears in the chat.
