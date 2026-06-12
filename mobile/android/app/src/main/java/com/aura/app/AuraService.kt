package com.aura.app

import android.app.*
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import kotlin.concurrent.thread

class AuraService : Service() {
    private val CHANNEL_ID = "AuraEngineChannel"
    private var isListening = false
    private lateinit var whisperEngine: WhisperEngine
    
    // ⚡ BOLT: 5-second circular buffer (16kHz, Mono)
    private val SAMPLE_RATE = 16000
    private val BUFFER_SIZE_SECONDS = 5
    private val audioBuffer = FloatArray(SAMPLE_RATE * BUFFER_SIZE_SECONDS)
    private var bufferIndex = 0

    override fun onCreate() {
        super.onCreate()
        whisperEngine = WhisperEngine(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createNotificationChannel()
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Aura // Hands-Free Active")
            .setContentText("Listening for 'Wake Aura'...")
            .setSmallIcon(R.drawable.ic_aura_logo)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(1, notification)
        }
        
        startAudioLoop()
        return START_STICKY
    }

    private fun startAudioLoop() {
        if (isListening) return
        isListening = true
        
        thread {
            val minBufferSize = AudioRecord.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_FLOAT
            )
            
            val audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_FLOAT,
                minBufferSize
            )

            audioRecord.startRecording()
            val tempBuffer = FloatArray(minBufferSize)

            while (isListening) {
                val read = audioRecord.read(tempBuffer, 0, minBufferSize, AudioRecord.READ_BLOCKING)
                if (read > 0) {
                    // Update circular buffer
                    for (i in 0 until read) {
                        audioBuffer[bufferIndex] = tempBuffer[i]
                        bufferIndex = (bufferIndex + 1) % audioBuffer.size
                    }
                    
                    // 🧠 Phase 6.3.2: Simple Energy VAD (Voice Activity Detection)
                    val energy = tempBuffer.map { it * it }.average()
                    if (energy > 0.01) { // Threshold for "Speech"
                        android.util.Log.d("AuraAudio", "Speech activity detected (Energy: $energy)")
                        // Trigger transcription on the last 5 seconds
                        val transcription = whisperEngine.transcribe(audioBuffer)
                        // TODO: Broadcast result to UI
                    }
                }
            }
            audioRecord.stop()
            audioRecord.release()
        }
    }

    override fun onDestroy() {
        isListening = false
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        val name = "Aura Engine"
        val descriptionText = "Ensures background reasoning persistence."
        val importance = NotificationManager.IMPORTANCE_LOW
        val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
            description = descriptionText
        }
        val notificationManager: NotificationManager =
            getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.createNotificationChannel(channel)
    }
}
