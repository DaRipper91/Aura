package com.aura.app

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class AuraBridge {
    private var pythonEngine: PyObject? = null

    init {
        // Initialize Python environment (handled by Chaquopy in Application class context)
        if (!Python.isStarted()) {
            // Start Python - usually done in a custom Application class, placed here for brevity
            // Python.start(AndroidPlatform(context)) 
        }
        
        val py = Python.getInstance()
        // Loads core/engine.py from our shared directory
        val engineModule = py.getModule("engine")
        pythonEngine = engineModule.callAttr("AuraEngine")
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
