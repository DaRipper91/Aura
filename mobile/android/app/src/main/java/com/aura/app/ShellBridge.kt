package com.aura.app

import java.io.BufferedReader
import java.io.InputStreamReader

class ShellBridge {

    interface ShellCallback {
        fun onOutput(line: String)
        fun onComplete(exitCode: Int)
    }

    fun isShizukuAvailable(): Boolean {
        // Basic check if rish is in PATH
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("which", "rish"))
            process.waitFor() == 0
        } catch (e: Exception) {
            false
        }
    }

    fun execute(command: String, callback: ShellCallback) {
        Thread {
            try {
                // Execute via Shizuku rish wrapper
                val process = Runtime.getRuntime().exec(arrayOf("rish", "-c", command))
                val reader = BufferedReader(InputStreamReader(process.inputStream))
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    line?.let { callback.onOutput(it) }
                }
                
                val errorReader = BufferedReader(InputStreamReader(process.errorStream))
                while (errorReader.readLine().also { line = it } != null) {
                    line?.let { callback.onOutput("[STDERR] $it") }
                }
                
                val exitCode = process.waitFor()
                callback.onComplete(exitCode)
            } catch (e: Exception) {
                callback.onOutput("[ERROR] Failed to execute via Rish: ${e.message}")
                callback.onComplete(-1)
            }
        }.start()
    }
}
