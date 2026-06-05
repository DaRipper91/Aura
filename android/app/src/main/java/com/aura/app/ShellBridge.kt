package com.aura.app

import dev.rikka.shizuku.Shizuku
import dev.rikka.shizuku.ShizukuRemoteProcess
import java.io.BufferedReader
import java.io.InputStreamReader

class ShellBridge {

    interface ShellCallback {
        fun onOutput(line: String)
        fun onComplete(exitCode: Int)
    }

    fun isShizukuAvailable(): Boolean {
        return try {
            Shizuku.pingBinder() && Shizuku.checkSelfPermission() == android.content.pm.PackageManager.PERMISSION_GRANTED
        } catch (e: Exception) {
            false
        }
    }

    fun execute(command: String, callback: ShellCallback) {
        if (!isShizukuAvailable()) {
            callback.onOutput("[ERROR] Shizuku Not Authorized")
            callback.onComplete(-1)
            return
        }

        Thread {
            try {
                val process: ShizukuRemoteProcess = Shizuku.newProcess(arrayOf("sh", "-c", command), null, null)
                val reader = BufferedReader(InputStreamReader(process.inputStream))
                
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    callback.onOutput(line!!)
                }
                
                val exitCode = process.waitFor()
                callback.onComplete(exitCode)
            } catch (e: Exception) {
                callback.onOutput("[SHELL_ERROR] ${e.message}")
                callback.onComplete(-1)
            }
        }.start()
    }
}
