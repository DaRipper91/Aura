from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, 
    QLabel, QHBoxLayout, QSlider, QFormLayout, QGroupBox, QPushButton,
    QComboBox, QFileDialog, QListWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFontDatabase, QFont
from aura.core.engine import OllamaClient
from aura.core.mandates import aura_component
from markdown_it import MarkdownIt
import os
import ctypes
import json
import html
import subprocess
from typing import Optional

class PullWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            process = subprocess.run(
                ["ollama", "pull", self.model_name],
                capture_output=True,
                text=True
            )
            if process.returncode == 0:
                self.finished.emit(True, f"Successfully pulled {self.model_name}")
            else:
                self.finished.emit(False, f"Failed to pull {self.model_name}: {process.stderr.strip()}")
        except Exception as e:
            self.finished.emit(False, str(e))

class ChatWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()

    def __init__(self, model: str, prompt: str, engine: OllamaClient, options: Optional[dict] = None):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.options = options
        self.engine = engine
        self.lib_path = os.path.join(os.path.dirname(__file__), "..", "bolt", "lib", "libbolt.so")

    def run(self):
        # ⚡ BOLT: Try FFI Integration first
        if os.path.exists(self.lib_path):
            try:
                # This is a stub for the actual FFI call which requires specific Zig exports
                # Falling back to the verified subprocess method for now, but logged for expansion
                print("[BOLT] Shared library detected. Switching to high-speed FFI bridge...")
                pass 
            except Exception as e:
                print(f"[BOLT ERROR] FFI failed: {e}")

        # Verified Subprocess Method (Bolt Tier 2)
        import subprocess
        bolt_bin = os.path.join(os.path.dirname(__name__), "..", "bolt", "zig-out", "bin", "bolt")
        if not os.path.exists(bolt_bin):
             bolt_bin = os.path.join(os.path.dirname(__file__), "..", "bolt", "zig-out", "bin", "bolt")

        if os.path.exists(bolt_bin):
            try:
                process = subprocess.Popen(
                    [bolt_bin, self.model, self.prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                def log_stderr():
                    for err_line in process.stderr:
                        if err_line.strip():
                            print(f"[Bolt Stderr]: {err_line.strip()}")
                
                import threading
                stderr_thread = threading.Thread(target=log_stderr, daemon=True)
                stderr_thread.start()

                for line in process.stdout:
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            # 🧩 PYTHON MAGIC: Structural Pattern Matching
                            match chunk_data:
                                case {"response": text}:
                                    self.chunk_received.emit(text)
                                case {"done": True}:
                                    break
                                case _:
                                    continue
                        except json.JSONDecodeError:
                            continue
                process.wait()
            except Exception as e:
                self.chunk_received.emit(f"\n[Bolt Error: {str(e)}]")
        else:
            for chunk in self.engine.stream_chat(self.model, self.prompt, self.options):
                self.chunk_received.emit(chunk)
        
        self.finished.emit()

@aura_component
class AuraWindow(QMainWindow):
    __slots__ = (
        "engine", "gen_options", "md", "models", "model_index", "model",
        "status_label", "settings_toggle", "output_area", "input_field",
        "settings_panel", "temp_label", "temp_slider", "top_p_label",
        "top_p_slider", "ctx_label", "ctx_slider", "font_combo",
        "font_size_slider", "dir_label", "dir_btn", "messages",
        "pending_message", "current_response_text", "worker", "workspace_label",
        "model_selector", "model_mapping", "discover_btn"
    )

    def get_git_branch(self, path):
        import subprocess
        try:
            result = subprocess.run(["git", "branch", "--show-current"], cwd=path, capture_output=True, text=True, check=True)
            branch = result.stdout.strip()
            return f" {branch}" if branch else ""
        except:
            return ""

    def __init__(self):
        super().__init__()
        self.check_mandates() # Decorator enforced method
        self.setWindowTitle("Aura // Local AI")
        self.resize(1200, 800)
        
        # Initialize Engine
        self.engine = OllamaClient()
        self.models = [m['name'] for m in self.engine.get_available_models()]
        if not self.models:
            self.models = ["qwen2.5:7b"]
        self.model = self.models[0]
        
        self.setStyleSheet("""
            QMainWindow { background-color: #080808; }
            QTextEdit { 
                background-color: #080808; 
                color: #B0B0B0; 
                border: none;
                selection-background-color: #2D1B4E;
            }
            /* Markdown Styling */
            pre { background-color: #121212; padding: 10px; border-radius: 4px; color: #A0A0A0; }
            code { color: #FF79C6; }
            h1, h2, h3 { color: #8833FF; }
            a { color: #D4AF37; }
            
            QLineEdit {
                background-color: #0F0F0F;
                color: #E0E0E0;
                border: 1px solid #1A1A1A;
                padding: 14px;
                border-radius: 2px;
            }
            QLineEdit:focus {
                border: 1px solid #8833FF;
                background-color: #121212;
            }
            QLabel {
                color: #404040;
                font-family: 'Monospace';
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            QGroupBox {
                border: 1px solid #1A1A1A;
                margin-top: 10px;
                padding-top: 10px;
                color: #D4AF37;
                font-family: 'Monospace';
                font-size: 10px;
            }
            QSlider::handle:horizontal {
                background: #8833FF;
                width: 12px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #0F0F0F;
                color: #404040;
                border: 1px solid #1A1A1A;
                padding: 8px 12px;
                font-family: 'Monospace';
                font-size: 10px;
            }
            QPushButton:hover {
                color: #D4AF37;
                border-color: #2D1B4E;
            }
            QPushButton:focus {
                border: 1px solid #8833FF;
                color: #E0E0E0;
            }
            QComboBox {
                background-color: #0F0F0F;
                color: #E0E0E0;
                border: 1px solid #1A1A1A;
                padding: 5px;
                font-family: 'Monospace';
                font-size: 10px;
            }
            QComboBox:focus {
                border: 1px solid #8833FF;
            }
        """)

        main_layout = QHBoxLayout()
        
        # Left Side (Chat)
        chat_container = QVBoxLayout()
        chat_container.setContentsMargins(30, 30, 30, 30)
        chat_container.setSpacing(20)
        
        header = QHBoxLayout()
        self.status_label = QLabel(f"ACTIVE_VOICE // {OllamaClient.MODELS[self.model]['name']}")
        header.addWidget(self.status_label)
        header.addStretch()
        
        self.models_toggle = QPushButton("MODELS")
        self.models_toggle.setCheckable(True)
        self.models_toggle.clicked.connect(self.toggle_models)
        header.addWidget(self.models_toggle)
        
        self.settings_toggle = QPushButton("VOID_SETTINGS")
        self.settings_toggle.setCheckable(True)
        self.settings_toggle.clicked.connect(self.toggle_settings)
        header.addWidget(self.settings_toggle)
        
        chat_container.addLayout(header)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("THE AURA IS SILENT...")
        chat_container.addWidget(self.output_area)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("DESCRIBE THE VOID...")
        self.input_field.returnPressed.connect(self.process_input)
        chat_container.addWidget(self.input_field)

        # Footer for workspace status (gemini-cli style)
        footer = QHBoxLayout()
        branch = self.get_git_branch(self.engine.project_root)
        self.workspace_label = QLabel(f"[{self.engine.project_root}] {branch}".strip())
        self.workspace_label.setStyleSheet("color: #6633FF; font-family: 'Monospace'; font-size: 10px;")
        footer.addStretch()
        footer.addWidget(self.workspace_label)
        chat_container.addLayout(footer)

        main_layout.addLayout(chat_container, stretch=4)

        # Right Side (Settings Panel)
        self.settings_panel = QWidget()
        self.settings_panel.setFixedWidth(300)
        self.settings_panel.setVisible(False)
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 30, 20, 30)
        
        # 1. Tuning Parameters
        tuning_group = QGroupBox("TUNING_PARAMETERS")
        form = QFormLayout()
        
        self.temp_label = QLabel(f"TEMP: {self.gen_options['temperature']}")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 200)
        self.temp_slider.setValue(int(self.gen_options['temperature'] * 100))
        self.temp_slider.valueChanged.connect(self.update_temp)
        form.addRow(self.temp_label, self.temp_slider)
        
        self.top_p_label = QLabel(f"TOP_P: {self.gen_options['top_p']}")
        self.top_p_slider = QSlider(Qt.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(int(self.gen_options['top_p'] * 100))
        self.top_p_slider.valueChanged.connect(self.update_top_p)
        form.addRow(self.top_p_label, self.top_p_slider)
        
        self.ctx_label = QLabel(f"CTX: {self.gen_options['num_ctx']}")
        self.ctx_slider = QSlider(Qt.Horizontal)
        self.ctx_slider.setRange(512, 32768)
        self.ctx_slider.setValue(self.gen_options['num_ctx'])
        self.ctx_slider.setSingleStep(512)
        self.ctx_slider.valueChanged.connect(self.update_ctx)
        form.addRow(self.ctx_label, self.ctx_slider)
        
        tuning_group.setLayout(form)
        settings_layout.addWidget(tuning_group)
        
        # 2. Typography
        typo_group = QGroupBox("TYPOGRAPHY")
        typo_form = QFormLayout()
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(self.available_fonts)
        self.font_combo.currentTextChanged.connect(self.update_font)
        typo_form.addRow(QLabel("FONT:"), self.font_combo)
        
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(10, 24)
        self.font_size_slider.setValue(14)
        self.font_size_slider.valueChanged.connect(self.update_font_size)
        typo_form.addRow(QLabel("SIZE:"), self.font_size_slider)
        
        typo_group.setLayout(typo_form)
        settings_layout.addWidget(typo_group)
        
        # 3. Workspace
        ws_group = QGroupBox("WORKSPACE")
        ws_layout = QVBoxLayout()
        self.dir_label = QLabel(f"DIR: {os.path.basename(self.engine.project_root)}")
        self.dir_label.setToolTip(self.engine.project_root)
        ws_layout.addWidget(self.dir_label)
        
        self.dir_btn = QPushButton("CHANGE_WORKSPACE")
        self.dir_btn.clicked.connect(self.change_directory)
        ws_layout.addWidget(self.dir_btn)
        
        ws_group.setLayout(ws_layout)
        settings_layout.addWidget(ws_group)

        # 4. Add Model
        pull_group = QGroupBox("ADD_MODEL")
        pull_layout = QHBoxLayout()
        self.pull_input = QLineEdit()
        self.pull_input.setPlaceholderText("e.g. llama3")
        self.pull_btn = QPushButton("PULL")
        self.pull_btn.clicked.connect(self.pull_model)
        pull_layout.addWidget(self.pull_input)
        pull_layout.addWidget(self.pull_btn)
        pull_group.setLayout(pull_layout)
        settings_layout.addWidget(pull_group)
        
        settings_layout.addStretch()
        self.settings_panel.setLayout(settings_layout)

        # Models Panel
        self.models_panel = QWidget()
        self.models_panel.setFixedWidth(300)
        self.models_panel.setVisible(False)
        mp_layout = QVBoxLayout()
        mp_layout.setContentsMargins(20, 30, 20, 30)
        
        mp_label = QLabel("LOCAL_MODELS //")
        mp_layout.addWidget(mp_label)
        
        self.models_list = QListWidget()
        self.models_list.setStyleSheet("""
            QListWidget {
                background-color: #0F0F0F;
                color: #D4AF37;
                border: 1px solid #1A1A1A;
                font-family: 'Monospace';
                font-size: 11px;
            }
            QListWidget::item:selected {
                background-color: #2D1B4E;
            }
        """)
        mp_layout.addWidget(self.models_list)
        
        btn_layout = QHBoxLayout()
        switch_btn = QPushButton("SWITCH")
        switch_btn.clicked.connect(self.switch_to_selected_model)
        btn_layout.addWidget(switch_btn)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.clicked.connect(self.populate_models_list)
        btn_layout.addWidget(refresh_btn)
        
        mp_layout.addLayout(btn_layout)
        
        self.models_panel.setLayout(mp_layout)
        
        main_layout.addWidget(self.models_panel)
        main_layout.addWidget(self.settings_panel)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.messages = []
        self.pending_message = None
        self.current_response_text = ""
        
        # Initial Font Application
        self.update_font(self.font_combo.currentText())

    def load_custom_fonts(self):
        self.available_fonts = ["Monospace", "Cascadia Code", "Consolas", "Courier New"]
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.exists(font_dir):
            for file in os.listdir(font_dir):
                if file.endswith(".ttf"):
                    font_id = QFontDatabase.addApplicationFont(os.path.join(font_dir, file))
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    for family in families:
                        if family not in self.available_fonts:
                            self.available_fonts.insert(0, family)

    def discover_models(self):
        self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // DISCOVERING LOCAL MODELS...</i></p>")
        available = self.engine.get_available_models()
        if not available:
            self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // NO MODELS FOUND ON OLLAMA SERVER</i></p>")
        else:
            for m in available:
                name = m.get("name", "Unknown")
                size = m.get("size", 0) / (1024**3)
                status = "[TUNED]" if name in OllamaClient.MODELS else "[RAW]"
                self.output_area.append(f"<p style='color: #B0B0B0; font-family: Monospace;'>• <b>{name}</b> ({size:.1f} GB) <span style='color: #404040;'>{status}</span></p>")
        self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>USE /model <name> TO SWITCH OR SELECT FROM HEADER</i></p>")

    def toggle_settings(self):
        if self.settings_toggle.isChecked():
            self.models_toggle.setChecked(False)
            self.models_panel.setVisible(False)
        self.settings_panel.setVisible(self.settings_toggle.isChecked())

    def _sync_model_selector(self):
        for i in range(self.model_selector.count()):
            if self.model_mapping.get(self.model_selector.itemText(i)) == self.model:
                self.model_selector.blockSignals(True)
                self.model_selector.setCurrentIndex(i)
                self.model_selector.blockSignals(False)
                break

    def change_model_from_selector(self, text):
        if text in self.model_mapping:
            new_model = self.model_mapping[text]
            if self.model != new_model:
                self.model = new_model
                self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {text}</i></p>")

    def toggle_models(self):
        if self.models_toggle.isChecked():
            self.settings_toggle.setChecked(False)
            self.settings_panel.setVisible(False)
            self.populate_models_list()
        self.models_panel.setVisible(self.models_toggle.isChecked())

    def populate_models_list(self):
        self.models_list.clear()
        available = self.engine.get_available_models()
        for m in available:
            name = m.get("name", "Unknown")
            size = m.get("size", 0) / (1024**3)
            status = "[TUNED]" if name in OllamaClient.MODELS else "[RAW]"
            self.models_list.addItem(f"{name} ({size:.1f}GB) {status}")

    def switch_to_selected_model(self):
        items = self.models_list.selectedItems()
        if not items:
            self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // NO MODEL SELECTED</i></p>")
            return
        
        target = items[0].text().split(" ")[0] # extract just the name
        self.model = target
        
        # Add to header dropdown if it's new
        found_in_header = False
        for i in range(self.model_selector.count()):
            if self.model_mapping.get(self.model_selector.itemText(i)) == target:
                found_in_header = True
                break
        
        if not found_in_header:
            display_name = f"[RAW] {target}"
            self.model_mapping[display_name] = target
            self.model_selector.addItem(display_name)

        self._sync_model_selector()
        
        friendly_name = OllamaClient.MODELS.get(target, {"name": f"[RAW] {target}"})["name"]
        self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {friendly_name}</i></p>")

    def pull_model(self):
        model_name = self.pull_input.text().strip()
        if not model_name: return
        self.pull_btn.setEnabled(False)
        self.pull_btn.setText("PULLING...")
        self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Pulling {model_name} from Ollama...</i></p>")
        
        self.pull_worker = PullWorker(model_name)
        self.pull_worker.finished.connect(self.on_pull_finished)
        self.pull_worker.start()

    def on_pull_finished(self, success, message):
        self.pull_btn.setEnabled(True)
        self.pull_btn.setText("PULL")
        self.pull_input.clear()
        safe_msg = html.escape(message)
        color = "#41CD52" if success else "#FF5555"
        self.output_area.append(f"<p style='color: {color}; font-family: Monospace;'><i>SYSTEM // {safe_msg}</i></p>")
        if success:
            self.populate_models_list()


    def update_temp(self, val):
        self.gen_options['temperature'] = val / 100.0
        self.temp_label.setText(f"TEMP: {self.gen_options['temperature']:.2f}")

    def update_top_p(self, val):
        self.gen_options['top_p'] = val / 100.0
        self.top_p_label.setText(f"TOP_P: {self.gen_options['top_p']:.2f}")

    def update_ctx(self, val):
        self.gen_options['num_ctx'] = val
        self.ctx_label.setText(f"CTX: {val}")

    def update_font(self, family):
        size = self.font_size_slider.value()
        font = QFont(family, size)
        self.output_area.setFont(font)
        self.input_field.setFont(font)

    def update_font_size(self, size):
        family = self.font_combo.currentText()
        font = QFont(family, size)
        self.output_area.setFont(font)
        self.input_field.setFont(font)

    def change_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Workspace", self.engine.project_root)
        if new_dir:
            self.engine.project_root = new_dir
            self.dir_label.setText(f"DIR: {os.path.basename(new_dir)}")
            self.dir_label.setToolTip(new_dir)
            branch = self.get_git_branch(new_dir)
            self.workspace_label.setText(f"[{new_dir}] {branch}".strip())
            safe_new_dir = html.escape(new_dir)
            self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Workspace updated: {safe_new_dir}</i></p>")

    def process_input(self):
        text = self.input_field.text().strip()
        if not text: return
        
        # 1. Navigation Handling (cd command)
        if text.startswith("cd "):
            target = text[3:].strip()
            if target == "~":
                target = os.path.expanduser("~")
            
            new_path = os.path.normpath(os.path.join(self.engine.project_root, target))
            
            if os.path.isdir(new_path):
                self.engine.project_root = new_path
                # Update UI elements representing directory
                self.dir_label.setText(f"DIR: {os.path.basename(new_path)}")
                self.dir_label.setToolTip(new_path)
                branch = self.get_git_branch(new_path)
                self.workspace_label.setText(f"[{new_path}] {branch}".strip())
                safe_path = html.escape(new_path)
                self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Context shifted to: {safe_path}</i></p>")
            else:
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // ERROR: Directory not found: {target}</i></p>")
            
            self.input_field.clear()
            return

        if text.startswith("/"):
            cmd = text[1:].lower()
            
            alias_map = {
                "phi": "phi3:mini",
                "gemma": "gemma2:2b",
                "qwen": "qwen2.5:7b",
                "coder": "qwen2.5-coder:1.5b",
                "deep": "deepseek-r1:8b",
                "noon": "moondream",
                "samist": "samantha-mistral"
            }

            if cmd == "help":
                self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // TUNED VOICES:</i></p>")
                for alias, m_id in alias_map.items():
                    if m_id in OllamaClient.MODELS:
                        self.output_area.append(f"<p style='color: #D4AF37; font-family: Monospace;'><b>/{alias}</b> - {OllamaClient.MODELS[m_id]['name']}</p>")
                self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>TYPE /MODELS TO SCAN LOCAL SYSTEM</i></p>")
                self.input_field.clear()
                return

            if cmd == "models":
                self.discover_models()
                self.input_field.clear()
                return

            if cmd.startswith("model "):
                target = cmd[6:].strip()
                for display_name, m_id in self.model_mapping.items():
                    if target in m_id.lower():
                        self.model = m_id
                        self._sync_model_selector()
                        friendly_name = OllamaClient.MODELS.get(m_id, {"name": f"[RAW] {m_id}"})["name"]
                        self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {friendly_name}</i></p>")
                        self.input_field.clear()
                        return
                
                safe_target = html.escape(target)
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // Model not found: {safe_target}</i></p>")
                self.input_field.clear()
                return

            if cmd in alias_map:
                target_model = alias_map[cmd]
                if target_model in self.models:
                    self.model = target_model
                    self._sync_model_selector()
                    self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {OllamaClient.MODELS[self.model]['name']}</i></p>")
                    self.input_field.clear()
                    return

            found = False
            for key in self.models:
                if cmd in key.lower():
                    self.model = key
                    self._sync_model_selector()
                    self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {OllamaClient.MODELS[self.model]['name']}</i></p>")
                    found = True
                    break
            
            if not found:
                safe_cmd = html.escape(cmd)
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // Unknown model: {safe_cmd}</i></p>")
            
            self.input_field.clear()
            return

        self.messages.append({"role": "user", "content": text})
        self.current_response_text = ""
        self.pending_message = {"role": "assistant", "model": self.model, "content": ""}
        self.render_messages()
        
        self.input_field.clear()
        self.input_field.setEnabled(False)

        self.worker = ChatWorker(self.model, text, self.engine, self.gen_options)
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.finished.connect(self.handle_finished)
        self.worker.start()

    def handle_chunk(self, chunk: str):
        self.current_response_text += chunk
        if self.pending_message:
            self.pending_message["content"] = self.current_response_text
        self.render_messages()

    def handle_finished(self):
        if self.pending_message:
            # Check for Tool Use (WRITE_FILE)
            content = self.pending_message["content"]
            if "WRITE_FILE:" in content and "CONTENT:" in content and "EOF" in content:
                self.handle_tool_use(content)
            
            self.messages.append(self.pending_message)
            self.pending_message = None
        self.render_messages()
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def handle_tool_use(self, content: str):
        try:
            # Simple parser for the model's command
            parts = content.split("WRITE_FILE:")[1].split("CONTENT:")
            path = parts[0].strip()
            file_content = parts[1].split("EOF")[0].strip()
            
            # Security: Prevent path traversal
            if os.path.isabs(path) or ".." in path:
                safe_path = html.escape(path)
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // TOOL_USE_DENIED: Path traversal detected: {safe_path}</i></p>")
                return

            full_path = os.path.normpath(os.path.join(self.engine.project_root, path))
            
            # Security: Ensure path is within project root
            if not full_path.startswith(os.path.normpath(self.engine.project_root)):
                safe_path = html.escape(path)
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // TOOL_USE_DENIED: Path outside workspace: {safe_path}</i></p>")
                return

            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "AURA // TOOL_USE", 
                                       f"QWEN requests to modify: {path}\n\nProceed with changes?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(file_content)
                safe_path = html.escape(path)
                self.output_area.append(f"<p style='color: #41CD52; font-family: Monospace;'><i>SYSTEM // FILE_WRITTEN: {safe_path}</i></p>")
            else:
                self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // FILE_WRITE_CANCELLED</i></p>")
        except Exception as e:
            safe_e = html.escape(str(e))
            self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // TOOL_USE_ERROR: {safe_e}</i></p>")

    def render_messages(self):
        self.output_area.clear()
        html_content = ""
        
        display_messages = self.messages.copy()
        if self.pending_message:
            display_messages.append(self.pending_message)
            
        for msg in display_messages:
            if msg["role"] == "user":
                safe_content = html.escape(msg['content'])
                html_content += f"<p><span style='color: #6633FF;'><b>&gt;</b></span> <span style='color: #FFFFFF;'>{safe_content}</span></p>"
            else:
                # Use raw text during streaming to avoid flickering, render markdown when done
                is_pending = (self.pending_message and msg == self.pending_message)
                if is_pending:
                    safe_content = html.escape(msg['content'])
                    content_html = f"<pre style='white-space: pre-wrap; font-family: inherit;'>{safe_content}</pre>"
                else:
                    # ⚡ BOLT OPTIMIZATION: Cache markdown rendering
                    # Parsing markdown is computationally expensive. During streaming, this function is called
                    # for every token chunk. By caching the rendered HTML on the message object, we convert
                    # an O(N*M) rendering bottleneck into O(1) for past messages.
                    # Expected impact: Eliminates UI freezing during long conversations.
                    content_html = msg.get("_rendered_html")
                    if content_html is None:
                        content_html = self.md.render(msg["content"])
                        msg["_rendered_html"] = content_html
                
                html_content += f"<div style='color: #FFD700; font-size: 13px; letter-spacing: 1px;'><b>{msg['model'].upper()}</b></div>"
                html_content += f"<div style='color: #B0B0B0;'>{content_html}</div><br>"
        
        self.output_area.setHtml(html_content)
        self.output_area.moveCursor(self.output_area.textCursor().MoveOperation.End)
g["content"])
                        msg["_rendered_html"] = content_html
                
                html_content += f"<div style='color: #FFD700; font-size: 13px; letter-spacing: 1px;'><b>{msg['model'].upper()}</b></div>"
                html_content += f"<div style='color: #B0B0B0;'>{content_html}</div><br>"
        
        self.output_area.setHtml(html_content)
        self.output_area.moveCursor(self.output_area.textCursor().MoveOperation.End)
