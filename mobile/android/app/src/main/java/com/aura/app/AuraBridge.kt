package com.aura.app

import android.os.Handler
import android.os.Looper
import com.chaquo.python.Python
import com.chaquo.python.PyObject
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * 🌉 AURA BRIDGE: The central interchange between Android UI, Python Hub, and Local Edge.
 */
class AuraBridge(private val context: android.content.Context) {
    private var pythonEngine: PyObject? = null
    private var localEngine: LocalInferenceEngine? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private var useLocalInference = false
    private val prefs = context.getSharedPreferences("aura_prefs", android.content.Context.MODE_PRIVATE)
    
    private val biometricHelper = if (context is androidx.fragment.app.FragmentActivity) BiometricHelper(context) else null
    private val modelManager = ModelManager(context)
    private val sensorBridge = SensorBridge(context)
    private var onEngineSwitch: ((Boolean) -> Unit)? = null

    init {
        localEngine = LocalInferenceEngine(context)
        try {
            val py = Python.getInstance()
            val engineModule = py.getModule("aura_core.engine")
            pythonEngine = engineModule.callAttr("OllamaClient")

            // 💾 PERSISTENCE: Load saved URL or use default
            val savedUrl = prefs.getString("orchestrator_url", "http://10.0.0.1:11434")
            pythonEngine?.callAttr("set_base_url", savedUrl)

            // 🛡️ SENTINEL: Register Security Handler
            pythonEngine?.callAttr("register_security_handler", SecurityHandler())

            // 📡 FORGE: Register Telemetry Handler
            pythonEngine?.callAttr("register_telemetry_handler", TelemetryHandler())

            // 🧠 COLLECTIVE: Register Action Handler
            pythonEngine?.callAttr("register_action_handler", ActionHandler())
        } catch (e: Exception) {
            android.util.Log.e("AuraBridge", "Python Engine Initialization Failed: ${e.message}")
        }
    }

    /**
     * Internal handler passed to Python to execute dispatched tasks on the satellite.
     */
    inner class ActionHandler {
        fun __call__(tool: String, args: PyObject): String {
            return try {
                when (tool) {
                    "notify" -> {
                        val text = args.callAttr("get", "text", "Aura Alert").toString()
                        mainHandler.post {
                            android.widget.Toast.makeText(context, text, android.widget.Toast.LENGTH_LONG).show()
                        }
                        "Notification triggered on Satellite."
                    }
                    "vibrate" -> {
                        val pattern = longArrayOf(0, 100, 200, 100)
                        val vibrator = context.getSystemService(android.content.Context.VIBRATOR_SERVICE) as android.os.Vibrator
                        vibrator.vibrate(android.os.VibrationEffect.createWaveform(pattern, -1))
                        "Haptic pulse executed on Satellite."
                    }
                    else -> "Error: Action '$tool' not implemented on Satellite."
                }
            } catch (e: Exception) {
                "Satellite Action Error: ${e.message}"
            }
        }
    }

    /**
     * Internal handler passed to Python to fetch on-device sensor data.
     */
    inner class TelemetryHandler {
        fun __call__(fuzzed: Boolean): String {
            return sensorBridge.getTelemetry(fuzzed)
        }
    }

    /**
     * Internal handler passed to Python to manage biometric gating.
     */
    inner class SecurityHandler {
        fun __call__(toolName: String, challenge: String): PyObject? {
            val py = Python.getInstance()
            val resultDict = py.getBuiltins().callAttr("dict")
            
            if (biometricHelper == null) {
                resultDict.callAttr("__setitem__", "status", "ERROR")
                return resultDict
            }

            val latch = CountDownLatch(1)
            var authStatus = "REJECTED"
            var signature = ""

            mainHandler.post {
                biometricHelper.authenticateForTool(toolName, challenge, { sig ->
                    authStatus = "APPROVED"
                    signature = sig
                    latch.countDown()
                }, { _ ->
                    authStatus = "REJECTED"
                    latch.countDown()
                })
            }

            // Wait for user input (Max 60s)
            latch.await(60, TimeUnit.SECONDS)

            resultDict.callAttr("__setitem__", "status", authStatus)
            resultDict.callAttr("__setitem__", "signature", signature)
            return resultDict
        }
    }

    fun setOnEngineSwitchListener(listener: (Boolean) -> Unit) {
        onEngineSwitch = listener
    }

    /**
     * Pipes the prompt to the active engine (Python/Remote or Standalone/Local).
     * Includes automatic failover to local engine on network failure.
     */
    fun sendPrompt(prompt: String, model: String = "qwen2.5:7b", callback: (String) -> Unit) {
        if (useLocalInference) {
            localEngine?.generateResponse(prompt) { result, _ ->
                mainHandler.post { callback(result) }
            }
            return
        }

        Thread {
            try {
                // Chaquopy translates Python generators to Java Iterators
                val generator = pythonEngine?.callAttr("stream_chat", model, prompt)
                val iterator = generator?.callAttr("__iter__")
                
                var fullResponse = ""
                while (true) {
                    val chunk = iterator?.callAttr("__next__")?.toString() ?: break
                    fullResponse += chunk
                    
                    mainHandler.post {
                        callback(fullResponse) 
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("AuraBridge", "Remote Inference Failed: ${e.message}")
                
                mainHandler.post {
                    val localModelName = "PHI3_MINI"
                    if (modelManager.isModelInAssets(localModelName)) {
                        callback("SYSTEM: HUB_OFFLINE // INITIATING_EDGE_HANDOVER...")
                        
                        modelManager.extractModelFromAssets(localModelName) { success, _ ->
                            if (success) {
                                val modelFile = modelManager.getModelFile(localModelName)
                                setLocalMode(true, modelFile.absolutePath, { result, _ ->
                                    callback(result)
                                }) { ready ->
                                    if (ready) {
                                        onEngineSwitch?.invoke(true)
                                        sendPrompt(prompt, model, callback)
                                    } else {
                                        callback("SYSTEM: FAILOVER_ERROR // LOCAL_ENGINE_FAULT")
                                    }
                                }
                            } else {
                                callback("SYSTEM: FAILOVER_ERROR // ASSET_EXTRACTION_FAILED")
                            }
                        }
                    } else {
                        callback("SYSTEM: HUB_OFFLINE // NO_LOCAL_BACKUP_FOUND")
                    }
                }
            }
        }.start()
    }

    fun setOrchestratorUrl(url: String) {
        prefs.edit().putString("orchestrator_url", url).apply()
        pythonEngine?.callAttr("set_base_url", url)
    }

    fun getOrchestratorUrl(): String {
        return prefs.getString("orchestrator_url", "http://10.0.0.1:11434") ?: "http://10.0.0.1:11434"
    }

    fun testConnection(url: String, callback: (Boolean) -> Unit) {
        Thread {
            try {
                val connection = java.net.URL(url).openConnection() as java.net.HttpURLConnection
                connection.connectTimeout = 3000
                connection.readTimeout = 3000
                connection.requestMethod = "GET"
                val responseCode = connection.responseCode
                mainHandler.post { callback(responseCode == 200 || responseCode == 404) }
            } catch (e: Exception) {
                mainHandler.post { callback(false) }
            }
        }.start()
    }

    fun setLocalMode(enabled: Boolean, modelPath: String? = null, onPartialResult: (String, Boolean) -> Unit = { _, _ -> }, onReady: (Boolean) -> Unit = {}) {
        useLocalInference = enabled
        if (enabled && modelPath != null) {
            localEngine?.initialize(modelPath, onPartialResult) { success ->
                mainHandler.post { onReady(success) }
            }
        } else {
            onReady(true)
        }
    }

    fun wakeLogicHub(macAddress: String) {
        Thread {
            try {
                val bytes = getMacBytes(macAddress)
                val magicPacket = ByteArray(6 + 16 * bytes.size)
                for (i in 0..5) magicPacket[i] = 0xff.toByte()
                var i = 6
                while (i < magicPacket.size) {
                    System.arraycopy(bytes, 0, magicPacket, i, bytes.size)
                    i += bytes.size
                }
                
                val inetAddress = java.net.InetAddress.getByName("255.255.255.255")
                val packet = java.net.DatagramPacket(magicPacket, magicPacket.size, inetAddress, 9)
                val socket = java.net.DatagramSocket()
                socket.send(packet)
                socket.close()
            } catch (e: Exception) {
                android.util.Log.e("AuraBridge", "Failed to send WoL packet: ${e.message}")
            }
        }.start()
    }
    
    private fun getMacBytes(macStr: String): ByteArray {
        val bytes = ByteArray(6)
        val hex = macStr.split(":", "-")
        if (hex.size != 6) throw IllegalArgumentException("Invalid MAC address")
        for (i in 0..5) bytes[i] = Integer.parseInt(hex[i], 16).toByte()
        return bytes
    }
}
