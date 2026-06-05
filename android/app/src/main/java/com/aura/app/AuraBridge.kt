package com.aura.app

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class AuraBridge {
    private var pythonEngine: PyObject? = null

    init {
        val py = Python.getInstance()
        // Loads aura/core/engine.py (Full Python Build)
        val engineModule = py.getModule("aura.core.engine")
        pythonEngine = engineModule.callAttr("OllamaClient")
    }

    /**
     * Updates the base URL for the Python engine (Remote Bridge).
     */
    fun setOrchestratorUrl(url: String) {
        pythonEngine?.callAttr("set_base_url", url)
    }

    /**
     * Pipes the prompt to Python and returns streamed chunks via callback.
     */
    fun sendPrompt(prompt: String, callback: (String) -> Unit) {
        Thread {
            try {
                // Chaquopy translates Python generators to Java Iterators
                val generator = pythonEngine?.callAttr("stream_chat", prompt)
                val iterator = generator?.callAttr("__iter__")
                
                var fullResponse = ""
                while (true) {
                    // Pull the next chunk from the Python generator
                    val chunk = iterator?.callAttr("__next__")?.toString() ?: break
                    fullResponse += chunk
                    
                    // Push state update to the Compose UI
                    callback(fullResponse) 
                }
            } catch (e: Exception) {
                // Python StopIteration ends the loop; catch it silently
            }
        }.start()
    }
}
