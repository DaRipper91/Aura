package com.aura.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognizerIntent
import android.view.HapticFeedbackConstants
import android.view.View
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.biometric.BiometricPrompt
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import coil.compose.AsyncImage

class MainActivity : FragmentActivity() {
    private lateinit var auraBridge: AuraBridge
    private lateinit var biometricHelper: BiometricHelper
    private var speechCallback: ((String) -> Unit)? = null

    private val speechRecognizerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            data?.get(0)?.let { speechCallback?.invoke(it) }
        }
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            startSpeechRecognition()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        auraBridge = AuraBridge()
        biometricHelper = BiometricHelper(this)

        // 🔐 SECURE: Require biometric unlock on launch
        biometricHelper.authenticate {
            setupContent()
        }
    }

    private fun setupContent() {
        val sharedText = if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)
        } else null

        setContent {
            AuraTheme {
                ChatScreen(auraBridge, sharedText, ::launchSpeechRecognition)
            }
        }
    }

    private fun launchSpeechRecognition(onResult: (String) -> Unit) {
        speechCallback = onResult
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            startSpeechRecognition()
        } else {
            requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    private fun startSpeechRecognition() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Aura Listening...")
        }
        speechRecognizerLauncher.launch(intent)
    }
}

@Composable
fun AuraTheme(content: @Composable () -> Unit) {
    val jetBrainsMono = FontFamily(
        Font(R.font.jetbrains_mono, FontWeight.Normal)
    )

    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Color(0xFF0F0F0F), // Obsidian dark background
            surface = Color(0xFF1A1A1A),
            onPrimary = Color(0xFFD4AF37),  // Gold accent
            onSecondary = Color(0xFF8833FF) // Purple accent
        ),
        typography = Typography(
            bodyLarge = androidx.compose.ui.text.TextStyle(
                fontFamily = jetBrainsMono,
                fontWeight = FontWeight.Normal
            )
        ),
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(bridge: AuraBridge, initialPrompt: String? = null, onDictate: (((String) -> Unit) -> Unit)? = null) {
    var inputText by remember { mutableStateOf(initialPrompt ?: "") }
    var messages by remember { mutableStateOf(listOf<String>()) }
    var isRemote by remember { mutableStateOf(false) }
    val view = LocalView.current
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .imePadding() 
    ) {
        // 🌌 HEADER: Status and Remote Toggle
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("AURA // PIXEL_10_PRO", color = Color(0xFFD4AF37), style = MaterialTheme.typography.labelSmall)
            Text(
                text = if (isRemote) "SYNC: REMOTE" else "SYNC: LOCAL",
                color = if (isRemote) Color(0xFF8833FF) else Color.Gray,
                modifier = Modifier.clickable { 
                    isRemote = !isRemote
                    bridge.setOrchestratorUrl(if (isRemote) "http://192.168.1.100:11434" else "http://localhost:11434")
                },
                style = MaterialTheme.typography.labelSmall
            )
        }

        LazyColumn(
            modifier = Modifier.weight(1f).padding(horizontal = 16.dp),
            reverseLayout = true 
        ) {
            items(messages.reversed()) { msg ->
                Column {
                    Text(
                        text = msg, 
                        color = if (msg.startsWith("USER:")) Color(0xFFD4AF37) else Color(0xFFB0B0B0), 
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                    // 🖼️ COIL: Simple image detection (mocked logic for overhaul)
                    if (msg.contains("http") && (msg.contains(".png") || msg.contains(".jpg"))) {
                        AsyncImage(
                            model = msg.substringAfter("http").substringBefore(" ").let { "http$it" },
                            contentDescription = "Aura Rendered Asset",
                            modifier = Modifier.fillMaxWidth().height(200.dp).padding(vertical = 8.dp)
                        )
                    }
                }
            }
        }
        
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            TextField(
                value = inputText,
                onValueChange = { inputText = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Aura Command...", color = Color.Gray) },
                colors = TextFieldDefaults.textFieldColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    cursorColor = Color(0xFFD4AF37)
                )
            )
            Spacer(modifier = Modifier.width(8.dp))
            if (onDictate != null) {
                IconButton(onClick = { onDictate { result -> inputText = result } }) {
                    Text("🎙️", color = Color(0xFF8833FF))
                }
                Spacer(modifier = Modifier.width(8.dp))
            }
            Button(
                onClick = {
                    val prompt = inputText
                    if (prompt.isNotBlank()) {
                        // 🔋 PERSISTENCE: Start background service during reasoning
                        val serviceIntent = Intent(context, AuraService::class.java)
                        context.startForegroundService(serviceIntent)

                        // ⚡ HAPTIC: Tactical pulse on send
                        view.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
                        
                        messages = messages + "USER: $prompt"
                        messages = messages + "AURA: ..." 
                        inputText = ""
                        
                        bridge.sendPrompt(prompt) { currentStream ->
                            // ⚡ HAPTIC: Micro-pulse during typewriter effect
                            view.performHapticFeedback(HapticFeedbackConstants.TEXT_HANDLE_MOVE)
                            messages = messages.dropLast(1) + "AURA: $currentStream"
                        }
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.onSecondary)
            ) {
                Text("VOID", color = Color.White)
            }
        }
    }
}
