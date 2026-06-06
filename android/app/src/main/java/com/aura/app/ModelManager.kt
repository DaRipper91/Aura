package com.aura.app

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

class ModelManager(private val context: Context) {
    
    // Placeholder URLs for MediaPipe Quantized Models
    private val modelUrls = mapOf(
        "QWEN_1.5B" to "https://example.com/models/qwen_1.5b_cpu_gpu.bin",
        "GEMMA_2B" to "https://example.com/models/gemma_2b_cpu_gpu.bin"
    )

    fun getModelFile(modelName: String): File {
        return File(context.getExternalFilesDir(null), "$modelName.bin")
    }

    fun isModelDownloaded(modelName: String): Boolean {
        return getModelFile(modelName).exists()
    }

    fun isModelInAssets(modelName: String): Boolean {
        return try {
            context.assets.list("models")?.contains("$modelName.bin") ?: false
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Extracts a model from the APK assets to internal storage.
     * MediaPipe requires a file path on the filesystem.
     */
    fun extractModelFromAssets(modelName: String, onComplete: (Boolean) -> Unit) {
        val targetFile = getModelFile(modelName)
        if (targetFile.exists()) {
            onComplete(true)
            return
        }

        Thread {
            try {
                val assetPath = "models/$modelName.bin"
                val inputStream: InputStream = context.assets.open(assetPath)
                val outputStream = FileOutputStream(targetFile)
                
                val buffer = ByteArray(1024 * 8)
                var read: Int
                while (inputStream.read(buffer).also { read = it } != -1) {
                    outputStream.write(buffer, 0, read)
                }
                
                outputStream.flush()
                outputStream.close()
                inputStream.close()
                onComplete(true)
            } catch (e: Exception) {
                android.util.Log.e("AuraModel", "Asset Extraction Failed: ${e.message}")
                onComplete(false)
            }
        }.start()
    }

    fun downloadModel(modelName: String, onComplete: (Boolean) -> Unit) {
        val url = modelUrls[modelName] ?: return onComplete(false)
        val request = DownloadManager.Request(Uri.parse(url))
            .setTitle("Aura // Pulling Model")
            .setDescription("Downloading $modelName for standalone inference")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            .setDestinationInExternalFilesDir(context, null, "$modelName.bin")
            .setAllowedOverMetered(true)
            .setAllowedOverRoaming(true)

        val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        downloadManager.enqueue(request)
        
        Thread {
            while (!isModelDownloaded(modelName)) {
                Thread.sleep(2000)
            }
            onComplete(true)
        }.start()
    }
}
