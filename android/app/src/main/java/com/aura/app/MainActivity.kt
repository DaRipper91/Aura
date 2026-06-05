package com.aura.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    private lateinit var auraBridge: AuraBridge

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize the Python Bridge
        auraBridge = AuraBridge()

        setContent {
            AuraTheme {
                ChatScreen(auraBridge)
            }
        }
    }
}

@Composable
fun AuraTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Color(0xFF0F0F0F), // Obsidian dark background
            surface = Color(0xFF1A1A1A),
            onPrimary = Color(0xFFD4AF37),  // Gold accent
            onSecondary = Color(0xFF8833FF) // Purple accent
        ),
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(bridge: AuraBridge) {
    var inputText by remember { mutableStateOf("") }
    var messages by remember { mutableStateOf(listOf<String>()) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .imePadding() // ZERO UI layout fragmentation when keyboard opens
    ) {
        LazyColumn(
            modifier = Modifier.weight(1f).padding(16.dp),
            reverseLayout = true // Feeds messages from the bottom up
        ) {
            items(messages.reversed()) { msg ->
                Text(
                    text = msg, 
                    color = Color(0xFFB0B0B0), 
                    modifier = Modifier.padding(vertical = 4.dp)
                )
            }
        }
        
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp)
        ) {
            TextField(
                value = inputText,
                onValueChange = { inputText = it },
                modifier = Modifier.weight(1f),
                colors = TextFieldDefaults.textFieldColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    textColor = Color.White
                )
            )
            Button(
                onClick = {
                    val prompt = inputText
                    if (prompt.isNotBlank()) {
                        messages = messages + "USER: $prompt"
                        messages = messages + "AURA: ..." // Initial stream state
                        inputText = ""
                        
                        bridge.sendPrompt(prompt) { currentStream ->
                            // Update the final message in the list dynamically
                            messages = messages.dropLast(1) + "AURA: $currentStream"
                        }
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.onSecondary)
            ) {
                Text("SEND", color = Color.White)
            }
        }
    }
}
