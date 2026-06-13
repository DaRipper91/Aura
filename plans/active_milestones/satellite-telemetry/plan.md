# Technical Plan: satellite-telemetry

## 🔍 Analysis & Context
*   **Objective:** Design the 'System Telemetry Bridge' for the Aura Android Satellite to allow the Hub Agent to query real-time sensor data (battery, thermal, location, network) efficiently and securely.
*   **Affected Files:** 
    *   `mobile/android/app/src/main/java/com/aura/satellite/sensors/SensorBridge.kt` (New)
    *   `python/aura_core/tools/satellite_tools.py` (New or modified)
    *   `mobile/android/app/build.gradle` (Dependencies update for sensors/location if needed)
*   **Key Dependencies:** Chaquopy (for Python-Kotlin bridge), Android Location Services, Android BatteryManager, Android TelephonyManager.
*   **Risks/Edge Cases:** 
    *   Battery drain from frequent polling (violates BOLT mandate). Must use cached or passive listeners where possible.
    *   Leaking precise location without explicit authorization (violates SENTINEL mandate). Fuzzing is mandatory by default.
    *   Network state changes or missing permissions causing bridge failures.

## 📋 Task Execution (Parallel Groups)

### Group 1 (Parallel Execution - Independent Tasks)
- [ ] Task 1.A: Implement Kotlin `SensorBridge` data gathering logic (Battery, Thermal, Network).
- [ ] Task 1.B: Implement Kotlin `SensorBridge` location logic with SENTINEL fuzzing.
- [ ] Task 1.C: Define the `SatelliteTelemetry` JSON Schema and validation models in Python.

### Group 2 (Sequential Execution - Depends on Group 1)
- [ ] Task 2.A: Implement Chaquopy integration in `SensorBridge` and Python tool `check_satellite_sensors`.
- [ ] Task 2.B: Implement Biometric Gating for `require_precision=True` flag in the satellite Android module.

## 📝 Step-by-Step Implementation Details

### Prerequisites
*   Ensure Android `Manifest.xml` has required permissions (`ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION`, `ACCESS_NETWORK_STATE`, `READ_PHONE_STATE`).
*   Ensure Chaquopy is configured to expose `SensorBridge` to Python.

#### Task 1.A: Kotlin `SensorBridge` Basic Sensors
1.  **Step 1 (The Unit Test Harness):** Define the verification requirement.
    *   *Target File:* `mobile/android/app/src/test/java/com/aura/satellite/sensors/SensorBridgeTest.kt`
    *   *Test Cases to Write:* Mock `BatteryManager`, `PowerManager`, and `TelephonyManager`. Assert `getTelemetry()` parses correctly to JSON without location precision.
2.  **Step 2 (The Implementation):** Execute the core change.
    *   *Target File:* `mobile/android/app/src/main/java/com/aura/satellite/sensors/SensorBridge.kt`
    *   *Exact Change:* Create `SensorBridge` class. Implement `getBatteryData()` and `getNetworkSignal()`. Ensure BOLT efficiency by not registering active listeners unless polled, or caching frequent passive updates (e.g., reading sticky intents for battery).

#### Task 1.B: Kotlin `SensorBridge` Location & Fuzzing
1.  **Step 1 (The Unit Test Harness):** Define the verification requirement.
    *   *Target File:* `mobile/android/app/src/test/java/com/aura/satellite/sensors/SensorBridgeLocationTest.kt`
    *   *Test Cases to Write:* Provide a mocked precise location. Assert `getLocation(false)` truncates coordinates to 2 decimal places (approx 1.1km precision). Assert `getLocation(true)` returns exact coordinates.
2.  **Step 2 (The Implementation):** Execute the core change.
    *   *Target File:* `mobile/android/app/src/main/java/com/aura/satellite/sensors/SensorBridge.kt`
    *   *Exact Change:* Implement `getLocation(requirePrecision: Boolean)`. If `requirePrecision` is false, round latitude and longitude to 2 decimal places and strip altitude to ensure SENTINEL compliance.

#### Task 1.C: Python Telemetry Schema & Tool
1.  **Step 1 (The Unit Test Harness):** Define the verification requirement.
    *   *Target File:* `python/tests/test_satellite_tools.py`
    *   *Test Cases to Write:* Validate mock tool output against the JSON Schema.
2.  **Step 2 (The Implementation):** Execute the core change.
    *   *Target File:* `python/aura_core/tools/satellite_tools.py`
    *   *Exact Change:* Implement the Python tool signature for `check_satellite_sensors`.

### 🧪 Global Testing Strategy
*   **Unit Tests:** Verify Kotlin data classes serialize to exact JSON schema. Verify Python schema validator parses Kotlin output. Verify location fuzzing math accurately truncates precision.
*   **Integration Tests:** Start Chaquopy environment, call `check_satellite_sensors(False)` from Python, ensure Kotlin returns mocked fuzzed data.

## 🎯 Success Criteria
*   The JSON Schema correctly represents all required data points.
*   The Kotlin `SensorBridge` is designed for Chaquopy invocation and implements coordinate fuzzing.
*   The Python tool `check_satellite_sensors` is fully typed and documented.
*   Both BOLT (efficiency caching) and SENTINEL (security fuzzing by default) mandates are structurally enforced in the design.