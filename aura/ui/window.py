from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal
from aura.core.engine import OllamaClient
from markdown_it import MarkdownIt

class ChatWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()

    def __init__(self, model: str, prompt: str):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.client = OllamaClient()

    def run(self):
        for chunk in self.client.stream_chat(self.model, self.prompt):
            self.chunk_received.emit(chunk)
        self.finished.emit()

from PySide6.QtGui import QIcon
import os

class AuraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura // Local AI")
        self.resize(1000, 700)
        
        # Set Application Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.md = MarkdownIt()
        self.models = list(OllamaClient.MODELS.keys())
        self.model_index = 0
        self.model = self.models[self.model_index]
        
        self.setStyleSheet("""
            QMainWindow { background-color: #080808; }
            QTextEdit { 
                background-color: #080808; 
                color: #B0B0B0; 
                font-family: 'Cascadia Code', 'Consolas', 'Monospace'; 
                font-size: 14px;
                border: none;
                selection-background-color: #2D1B4E;
            }
            /* Markdown Styling */
            pre {
                background-color: #121212;
                padding: 10px;
                border-radius: 4px;
                color: #A0A0A0;
            }
            code {
                color: #FF79C6;
                font-family: 'Cascadia Code', 'Monospace';
            }
            h1, h2, h3 { color: #8833FF; }
            a { color: #D4AF37; }
            QLineEdit {
                background-color: #0F0F0F;
                color: #E0E0E0;
                font-family: 'Cascadia Code', 'Monospace';
                font-size: 14px;
                border: 1px solid #1A1A1A;
                padding: 14px;
                border-radius: 2px;
            }
            QLabel {
                color: #404040;
                font-family: 'Monospace';
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        self.status_label = QLabel(f"ACTIVE_VOICE // {OllamaClient.MODELS[self.model]['name']}")
        header.addWidget(self.status_label)
        header.addStretch()
        header.addWidget(QLabel("TYPE /MODEL TO SWITCH"))
        layout.addLayout(header)

        self.output_area = QTextEdit()
...
    def process_input(self):
        text = self.input_field.text().strip()
        if not text: return
        
        # Command Handling
        if text.startswith("/"):
            cmd = text[1:].lower()
            found = False
            for key in self.models:
                # Match partial names (e.g., /phi matches phi3:mini)
                if cmd in key.lower():
                    self.model = key
                    self.status_label.setText(f"ACTIVE_VOICE // {OllamaClient.MODELS[self.model]['name']}")
                    self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {OllamaClient.MODELS[self.model]['name']}</i></p>")
                    found = True
                    break
            
            if not found:
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // Unknown model: {cmd}</i></p>")
            
            self.input_field.clear()
            return

        self.messages.append({"role": "user", "content": text})
        self.render_messages()
        
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.current_response_text = ""

        self.worker = ChatWorker(self.model, text)
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.finished.connect(self.handle_finished)
        self.worker.start()

    def handle_chunk(self, chunk: str):
        self.current_response_text += chunk
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # If it's the first chunk of a response, add the model label
        if len(self.current_response_text) == len(chunk):
            self.output_area.append(f"<span style='color: #D4AF37;'><b>{self.model.upper()}</b></span>: ")
        
        cursor.insertText(chunk)
        self.output_area.setTextCursor(cursor)
        self.output_area.ensureCursorVisible()

    def handle_finished(self):
        self.messages.append({"role": "assistant", "model": self.model, "content": self.current_response_text})
        self.render_messages()
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def render_messages(self):
        self.output_area.clear()
        html_content = ""
        for msg in self.messages:
            if msg["role"] == "user":
                html_content += f"<p><span style='color: #6633FF;'><b>&gt;</b></span> <span style='color: #FFFFFF;'>{msg['content']}</span></p>"
            else:
                content_html = self.md.render(msg["content"])
                html_content += f"<div style='color: #D4AF37;'><b>{msg['model'].upper()}</b></div>"
                html_content += f"<div style='color: #B0B0B0;'>{content_html}</div><br>"
        
        self.output_area.setHtml(html_content)
        self.output_area.moveCursor(self.output_area.textCursor().MoveOperation.End)
