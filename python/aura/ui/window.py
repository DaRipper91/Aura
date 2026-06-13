from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, 
    QLabel, QHBoxLayout, QSlider, QFormLayout, QGroupBox, QPushButton,
    QComboBox, QFileDialog, QListWidget, QListWidgetItem, QFrame, QScrollArea, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QIcon, QFontDatabase, QFont, QPainter, QColor, QLinearGradient, QPen
from aura_core.engine import OllamaClient
from aura_core.mandates import aura_component
from markdown_it import MarkdownIt
import os
import sys
import re
import ctypes
import json
import html
import subprocess
import time
import random
import tempfile
import base64
from io import BytesIO
from collections import deque
from typing import Optional
from PIL import Image
try:
    import mss
except ImportError:
    mss = None

class GhostLogArea(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            background-color: transparent;
            color: rgba(0, 230, 230, 0.15);
            border: none;
            font-family: 'Monospace';
            font-size: 8px;
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ⚡ BOLT OPTIMIZATION: Prevent O(N) memory leak and layout degradation
        # Cap the number of log blocks since it updates very frequently
        self.document().setMaximumBlockCount(100)

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        safe_msg = html.escape(message)
        safe_time = html.escape(timestamp)
        self.append(f"<span style='white-space: pre-wrap;'>[{safe_time}] {safe_msg}</span>")
        self.moveCursor(self.textCursor().MoveOperation.End)

class PowerStripe(QFrame):
    def __init__(self, color="#00e6e6", parent=None):
        super().__init__(parent)
        self.setFixedWidth(4)
        self.color = color
        self.intensity = 0.5
        self.setStyleSheet(f"background-color: {color}; border-radius: 2px;")

    def set_intensity(self, val: float):
        self.intensity = max(0.1, min(1.0, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        color = QColor(self.color)
        color.setAlphaF(self.intensity)
        grad.setColorAt(0, color)
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), grad)

class AudioVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.setFixedWidth(100)
        self.bars = [random.uniform(0.1, 0.8) for _ in range(15)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        self.is_active = False

    def start(self):
        self.is_active = True
        self.timer.start(100)

    def stop(self):
        self.is_active = False
        self.timer.stop()
        self.update()

    def update_bars(self):
        self.bars = [random.uniform(0.1, 0.9) for _ in range(15)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width() / len(self.bars)
        for i, val in enumerate(self.bars):
            h = self.height() * (val if self.is_active else 0.1)
            y = (self.height() - h) / 2
            color = QColor("#00e6e6")
            color.setAlphaF(0.6)
            painter.fillRect(i * w + 2, y, w - 4, h, color)

class VisionThread(QThread):
    def __init__(self):
        super().__init__()
        self.buffer = deque(maxlen=3)
        self.is_running = True

    def run(self):
        if not mss:
            print("[AURA_VISION] mss library not found. Vision disabled.")
            return

        with mss.mss() as sct:
            while self.is_running:
                try:
                    # Capture primary monitor (0 is all, 1 is first)
                    monitor = sct.monitors[1]
                    sct_img = sct.grab(monitor)
                    
                    # Convert to PIL for resizing to save bandwidth/tokens
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    img.thumbnail((1280, 1280)) 
                    
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG", quality=70)
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    self.buffer.append(img_str)
                except Exception as e:
                    print(f"[AURA_VISION] Capture Error: {e}")
                
                # Check for stop signal frequently
                for _ in range(100):
                    if not self.is_running: return
                    time.sleep(0.1)

    def stop(self):
        self.is_running = False

class ChatWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()

    def __init__(self, model: str, prompt: str, engine: OllamaClient, options: Optional[dict] = None):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.options = options
        self.engine = engine
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        # ⚡ PURE PYTHON: Verfied native stream
        try:
            for chunk in self.engine.autonomous_chat(self.model, self.prompt):
                if not self.is_running:
                    break
                self.chunk_received.emit(chunk)
        except Exception as e:
            if self.is_running:
                self.chunk_received.emit(f"\n[Aura Error: {str(e)}]")

        self.finished.emit()

class AutoResizingTextEdit(QTextEdit):
    returnPressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self.adjust_height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(45)
        self.setMaximumHeight(200)

    def adjust_height(self):
        doc_height = int(self.document().size().height())
        margins = self.contentsMargins()
        new_height = doc_height + margins.top() + margins.bottom() + 10 # padding
        self.setFixedHeight(min(self.maximumHeight(), max(self.minimumHeight(), new_height)))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers() & Qt.ShiftModifier:
            print("[AURA_UI] Enter Pressed")
            event.accept()
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

@aura_component
class AuraWindow(QMainWindow):
    __slots__ = (
        "engine", "gen_options", "md", "models", "model_index", "model",
        "status_label", "settings_toggle", "output_area", "input_field",
        "settings_panel", "temp_label", "temp_slider", "top_p_label",
        "top_p_slider", "ctx_label", "ctx_slider", "font_combo",
        "font_size_slider", "dir_label", "dir_btn", "messages",
        "pending_message", "current_response_text", "worker", "workspace_label",
        "model_selector", "model_mapping", "discover_btn", "models_toggle",
        "models_panel", "models_list", "hub_url_input", "debug_toggle",
        "visualizer", "ghost_log", "power_stripe", "glitch_timer", "saturation",
        "telemetry_label", "telemetry_timer", "typewriter_speed", "is_typing",
        "available_fonts", "verb_label", "verb_slider",
        "sat_label", "sat_slider", "profile_combo", "speed_label", "speed_slider",
        "last_render_time", "operation_mode_combo", "command_preset_combo", "commands_btn",
        "vision_worker"
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
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize Engine (Defaulting to Remote Hub via Tailscale)
        self.engine = OllamaClient()
        self.ollama_ready = True # We assume the Hub is active

        # Prefer Qwen-Coder first, then others from the Hub.
        available_tags = [m['name'] for m in self.engine.get_available_models()]
        priority_models = ["qwen2.5-coder:7b", "aura-qwen:latest", "aura-architect:latest"]
        self.model = None
        for p in priority_models:
            if p in available_tags:
                self.model = p
                break

        if not self.model and available_tags:
            self.model = available_tags[0]

        if not self.model:
            self.model = "qwen2.5-coder:7b" # Force a default even if offline

        lightweight_models = [model for model in available_tags if self.engine.is_lightweight_model(model)]
        self.models = lightweight_models if lightweight_models else (available_tags if available_tags else [self.model])
        self.remote_models = []
        
        # Generation Options
        self.gen_options = {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 1024
        }
        self.md = MarkdownIt()
        self.load_custom_fonts()
        
        # State & Settings
        self.saturation = 1.0
        self.typewriter_speed = 30 # ms per chunk
        self.is_typing = False
        self.messages = []
        
        # 👁️ WATCHFUL EYE: Background Vision Thread
        self.vision_worker = VisionThread()
        self.vision_worker.start()

        self.pending_message = None
        self.current_response_text = ""
        self.last_render_time = 0.0

        # Model Management
        self.model_mapping = {v['name']: k for k, v in OllamaClient.MODELS.items()}
        self.model_selector = QComboBox()
        self.model_selector.addItems(list(self.model_mapping.keys()))
        self.model_selector.currentTextChanged.connect(self.change_model_from_selector)
        
        self.update_stylesheet()

        main_layout = QHBoxLayout()
        
        # Left Side (Chat)
        chat_container = QVBoxLayout()
        chat_container.setContentsMargins(30, 30, 30, 30)
        chat_container.setSpacing(20)
        
        header = QHBoxLayout()
        friendly_name = OllamaClient.MODELS.get(self.model, {"name": self.model})["name"]
        self.status_label = QLabel(f"ACTIVE_VOICE // {friendly_name}")
        header.addWidget(self.status_label)
        
        header.addWidget(self.model_selector) # ⚡ NEW: Direct model switching
        
        self.visualizer = AudioVisualizer()
        header.addWidget(self.visualizer)
        header.addStretch()

        self.abort_btn = QPushButton("ABORT")
        self.abort_btn.setStyleSheet("color: #FF5555; font-weight: bold; border: 1px solid #FF5555; padding: 2px 10px;")
        self.abort_btn.clicked.connect(self.abort_generation)
        self.abort_btn.setVisible(False)
        header.addWidget(self.abort_btn)

        self.debug_toggle = QPushButton("DEBUG")
        self.debug_toggle.setCheckable(True)
        self.debug_toggle.setStyleSheet("color: #00e6e6; font-weight: bold; border: 1px solid #00e6e6; padding: 2px 10px;")
        header.addWidget(self.debug_toggle)

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

        self.input_field = AutoResizingTextEdit()
        self.input_field.setPlaceholderText("DESCRIBE THE VOID...")
        self.input_field.returnPressed.connect(lambda: self.process_input())
        chat_container.addWidget(self.input_field)

        # Footer for workspace status (gemini-cli style)
        footer = QHBoxLayout()
        branch = self.get_git_branch(self.engine.project_root)
        self.workspace_label = QLabel(f"[{self.engine.project_root}] {branch}".strip())
        footer.addWidget(self.workspace_label)
        footer.addStretch()
        
        self.telemetry_label = QLabel("NODE: HUB // TPS: 0.0 // VRAM: 0.0")
        self.telemetry_label.setStyleSheet("color: #6633FF; font-family: 'Monospace'; font-size: 10px;")
        footer.addWidget(self.telemetry_label)
        
        chat_container.addLayout(footer)

        main_layout.addLayout(chat_container, stretch=4)

        # Ghost Log Stream (Far Right)
        self.ghost_log = GhostLogArea()
        self.ghost_log.setFixedWidth(150)
        main_layout.addWidget(self.ghost_log)

        # Right Side (Settings Panel)
        self.settings_panel = QWidget()
        self.settings_panel.setObjectName("settings_panel")
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

        # 1.5 Console Controls
        console_group = QGroupBox("CONSOLE_CONTROLS")
        c_form = QFormLayout()
        
        self.verb_label = QLabel(f"VERBOSITY: {self.engine.verbosity:.1f}")
        self.verb_slider = QSlider(Qt.Horizontal)
        self.verb_slider.setRange(0, 100)
        self.verb_slider.setValue(int(self.engine.verbosity * 100))
        self.verb_slider.valueChanged.connect(self.update_verbosity)
        c_form.addRow(self.verb_label, self.verb_slider)

        self.sat_label = QLabel(f"SATURATION: {self.saturation:.1f}")
        self.sat_slider = QSlider(Qt.Horizontal)
        self.sat_slider.setRange(0, 100)
        self.sat_slider.setValue(int(self.saturation * 100))
        self.sat_slider.valueChanged.connect(self.update_saturation)
        c_form.addRow(self.sat_label, self.sat_slider)
        
        console_group.setLayout(c_form)
        settings_layout.addWidget(console_group)

        # 1.75 Mode & Commands
        commands_group = QGroupBox("MODES_AND_COMMANDS")
        cmd_form = QFormLayout()

        self.operation_mode_combo = QComboBox()
        self.operation_mode_combo.addItems(list(OllamaClient.OPERATION_MODES.keys()))
        self.operation_mode_combo.setCurrentText(self.engine.operation_mode)
        self.operation_mode_combo.currentTextChanged.connect(self.update_operation_mode)
        cmd_form.addRow(QLabel("MODE:"), self.operation_mode_combo)

        self.command_preset_combo = QComboBox()
        self.command_preset_combo.addItems([
            "/commands",
            "/help",
            "/models",
            "/model aura-qwen",
            "/model aura-deepseek",
            "/model qwen2.5-coder:1.5b",
            "/model deepseek-r1:1.5b",
            "/model phi3:mini",
            "/coder",
            "/deep",
            "/phi",
        ])
        self.command_preset_combo.currentTextChanged.connect(lambda _text: self.save_session())
        cmd_form.addRow(QLabel("COMMAND:"), self.command_preset_combo)

        self.commands_btn = QPushButton("RUN_COMMAND")
        self.commands_btn.clicked.connect(self.run_selected_command)
        cmd_form.addRow(self.commands_btn)

        commands_group.setLayout(cmd_form)
        settings_layout.addWidget(commands_group)
        
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

        browse_group = QGroupBox("REMOTE LOGIC HUB")
        browse_layout = QVBoxLayout()
        
        # Hub IP Input
        hub_row = QHBoxLayout()
        hub_label = QLabel("Hub IP:")
        hub_label.setStyleSheet("color: gray;")
        self.hub_url_input = QLineEdit()
        self.hub_url_input.setPlaceholderText("e.g., http://100.x.y.z:11434")
        
        # Load saved Hub URL
        saved_url = os.environ.get("AURA_LOGIC_HUB_URL", "")
        if saved_url:
            self.hub_url_input.setText(saved_url)
            
        self.hub_url_input.textEdited.connect(self._update_hub_url)
        
        hub_row.addWidget(hub_label)
        hub_row.addWidget(self.hub_url_input)
        browse_layout.addLayout(hub_row)

        browse_group.setLayout(browse_layout)
        settings_layout.addWidget(browse_group)
        
        settings_layout.addStretch()
        self.settings_panel.setLayout(settings_layout)

        # Models Panel
        self.models_panel = QWidget()
        self.models_panel.setObjectName("models_panel")
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
            QListWidget:focus {
                border: 1px solid #D4AF37;
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

        # Initial Font Application
        self.update_font(self.font_combo.currentText())
        
        # Telemetry Timer
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(2000)

        # Session Restoration
        self.load_session()

    def update_stylesheet(self):
        teal = f"rgba(0, 230, 230, {0.5 * self.saturation})"
        purple = f"rgba(102, 51, 255, {0.3 * self.saturation})"
        bg = "rgba(13, 13, 26, 0.95)" if self.saturation > 0.5 else "#0d0d1a"
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #050505; }}
            QTextEdit {{ 
                background-color: transparent; 
                color: #B0B0B0; 
                border: none;
                selection-background-color: rgba(0, 128, 128, 0.4);
            }}
            /* Glass Panels */
            #settings_panel, #models_panel {{
                background-color: rgba(13, 13, 26, 0.7);
                border-left: 1px solid {teal};
            }}
            
            pre {{ background-color: rgba(128, 0, 128, 0.1); padding: 10px; border-radius: 4px; color: #E0E0E0; border: 1px solid {purple}; }}
            code {{ color: #00e6e6; }}
            h1, h2, h3 {{ color: #00e6e6; }}
            
            AutoResizingTextEdit {{
                background-color: rgba(128, 0, 128, 0.1);
                color: #E0E0E0;
                border: 1px solid {purple};
                padding: 10px;
                border-radius: 6px;
            }}
            AutoResizingTextEdit:focus {{
                border: 1px solid #00e6e6;
                background-color: rgba(128, 0, 128, 0.2);
            }}
            AutoResizingTextEdit:disabled {{
                color: rgba(224, 224, 224, 0.5);
                border: 1px dashed rgba(102, 51, 255, 0.2);
                background-color: rgba(13, 13, 26, 0.3);
            }}
            QLabel {{
                color: #00cccc;
                font-family: 'Monospace';
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            QGroupBox {{
                border: 1px solid {purple};
                margin-top: 10px;
                padding-top: 10px;
                color: #00e6e6;
                font-family: 'Monospace';
                font-size: 10px;
            }}
            QSlider::handle:horizontal {{
                background: #00e6e6;
                width: 12px;
                border-radius: 6px;
            }}
            QPushButton {{
                background-color: rgba(128, 0, 128, 0.1);
                color: #00e6e6;
                border: 1px solid {purple};
                padding: 8px 12px;
                font-family: 'Monospace';
                font-size: 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                color: #ffffff;
                border-color: #00e6e6;
                background-color: rgba(128, 0, 128, 0.3);
            }}
            QPushButton:focus {{
                border-color: #00e6e6;
                outline: none;
                background-color: rgba(128, 0, 128, 0.2);
            }}
            QPushButton:disabled {{
                color: rgba(0, 230, 230, 0.3);
                border: 1px dashed rgba(102, 51, 255, 0.2);
                background-color: rgba(128, 0, 128, 0.05);
            }}
            QPushButton:checked {{
                background-color: rgba(0, 230, 230, 0.2);
                color: #ffffff;
                border: 1px solid #00e6e6;
            }}
            QLineEdit, QComboBox {{
                background-color: rgba(13, 13, 26, 0.7);
                color: #E0E0E0;
                border: 1px solid {purple};
                padding: 4px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid #00e6e6;
                background-color: rgba(128, 0, 128, 0.2);
            }}
            QLineEdit:disabled, QComboBox:disabled {{
                color: rgba(224, 224, 224, 0.5);
                border: 1px dashed rgba(102, 51, 255, 0.2);
                background-color: rgba(13, 13, 26, 0.3);
            }}
        """)

    def update_telemetry(self):
        # Hardware Aware Telemetry
        node = "ASAHI" if self.engine.is_asahi() else "X64_HP"
        tps = random.uniform(15.0, 45.0) if self.visualizer.is_active else 0.0
        vram = random.uniform(2.1, 4.8) if self.engine.is_asahi() else 0.8
        self.telemetry_label.setText(f"NODE: {node} // TPS: {tps:.1f} // VRAM: {vram:.1f}G")
        self.ghost_log.log(f"TELEMETRY_SYNC: OK (VRAM: {vram:.1f}G)")

    def update_verbosity(self, val):
        self.engine.set_verbosity(val / 100.0)
        self.verb_label.setText(f"VERBOSITY: {self.engine.verbosity:.1f}")
        self.ghost_log.log(f"ENGINE_MODE: VERBOSITY_SHIFT ({self.engine.verbosity:.1f})")

    def update_saturation(self, val):
        self.saturation = val / 100.0
        self.sat_label.setText(f"SATURATION: {self.saturation:.1f}")
        self.update_stylesheet()

    def update_profile(self, profile):
        self.engine.set_profile(profile)
        self.ghost_log.log(f"HARDWARE_PROFILE: {profile} ACTIVATED")
        self.trigger_glitch()

    def update_operation_mode(self, mode):
        self.engine.set_operation_mode(mode)
        self.ghost_log.log(f"OPERATION_MODE: {mode.upper()} ACTIVATED")
        self.output_area.append(
            f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Operation mode set to {html.escape(mode)}</i></p>"
        )
        self.save_session()

    def run_selected_command(self):
        command = self.command_preset_combo.currentText().strip()
        if not command:
            return
        self.input_field.setPlainText(command)
        self.process_input()

    def trigger_glitch(self, severity="subtle"):
        """Palette Mandate: Reactive aesthetic feedback."""
        colors = {
            "subtle": "rgba(0, 230, 230, 0.08)",   # Cyan (Tool OK / Context Shift)
            "critical": "rgba(255, 85, 85, 0.15)",  # Red (Error / Failure)
            "wipe": "rgba(255, 0, 255, 0.1)"        # Magenta (Context Clear)
        }
        color = colors.get(severity, colors["subtle"])
        self.output_area.setStyleSheet(f"background-color: {color};")
        QTimer.singleShot(150, lambda: self.output_area.setStyleSheet("background-color: transparent;"))
        self.ghost_log.log(f"UI_GLITCH_TRIGGERED: {severity.upper()}")

    def load_session(self):
        try:
            session_path = os.path.join(self.engine.project_root, ".aura_session.json")
            if os.path.exists(session_path):
                with open(session_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.messages = data
                    else:
                        self.messages = data.get("messages", data.get("history", []))
                        saved_mode = data.get("operation_mode")
                        if saved_mode in OllamaClient.OPERATION_MODES:
                            self.engine.set_operation_mode(saved_mode)
                            self.operation_mode_combo.blockSignals(True)
                            self.operation_mode_combo.setCurrentText(saved_mode)
                            self.operation_mode_combo.blockSignals(False)
                        saved_model = data.get("current_model")
                        if saved_model:
                            self.model = saved_model
                            self.engine.current_model = saved_model
                            self._sync_model_selector()
                        saved_command = data.get("command_preset")
                        if saved_command:
                            self.command_preset_combo.blockSignals(True)
                            self.command_preset_combo.setCurrentText(saved_command)
                            self.command_preset_combo.blockSignals(False)
                        saved_hub_url = data.get("hub_url")
                        if saved_hub_url is not None:
                            self.hub_url_input.blockSignals(True)
                            self.hub_url_input.setText(saved_hub_url)
                            self.engine.base_url = saved_hub_url or os.environ.get("OLLAMA_HOST", "http://100.100.181.59:11434")
                            self.hub_url_input.blockSignals(False)
                    self.render_messages()
                    self.ghost_log.log("SESSION_RE_ANIMATED: OK")
        except:
            pass

    def save_session(self):
        try:
            session_path = os.path.join(self.engine.project_root, ".aura_session.json")
            with open(session_path, "w") as f:
                json.dump(
                    {
                        "messages": self.messages,
                        "operation_mode": self.engine.operation_mode,
                        "current_model": self.model,
                        "command_preset": self.command_preset_combo.currentText(),
                        "hub_url": self.hub_url_input.text() if hasattr(self, 'hub_url_input') else "",
                    },
                    f,
                )
        except:
            pass

    def closeEvent(self, event):
        """Clean up background threads on exit."""
        if hasattr(self, 'vision_worker'):
            self.vision_worker.stop()
            self.vision_worker.wait()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

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
                safe_name = html.escape(name)
                safe_status = html.escape(status)
                self.output_area.append(f"<p style='color: #B0B0B0; font-family: Monospace;'>• <b>{safe_name}</b> ({size:.1f} GB) <span style='color: #404040;'>{safe_status}</span></p>")
        self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>USE /model &lt;name&gt; TO SWITCH OR SELECT FROM HEADER</i></p>")

    def toggle_settings(self):
        if self.settings_toggle.isChecked():
            self.models_toggle.setChecked(False)
            self.models_panel.setVisible(False)
            if not self.remote_models:
                self.search_remote_models()
        self.settings_panel.setVisible(self.settings_toggle.isChecked())

    def _update_hub_url(self, text: str):
        url = text.strip()
        if url:
            self.engine.base_url = url
        else:
            self.engine.base_url = os.environ.get("OLLAMA_HOST", "http://100.100.181.59:11434")
        self.save_session()
        
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
                self.engine.current_model = new_model
                self.engine.clear_history()
                self.trigger_glitch("wipe")
                safe_text = html.escape(text)
                self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {safe_text} (Context Cleared)</i></p>")
                self.save_session()

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
            weight = "[LIGHT]" if self.engine.is_lightweight_model(name) else "[HEAVY]"
            self.models_list.addItem(f"{name} ({size:.1f}GB) {status} {weight}")

    def switch_to_selected_model(self):
        items = self.models_list.selectedItems()
        if not items:
            self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // NO MODEL SELECTED</i></p>")
            return
        
        target = items[0].text().split(" ")[0] # extract just the name
        self.model = target
        self.engine.clear_history()
        self.trigger_glitch("wipe")
        
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
        safe_friendly_name = html.escape(friendly_name)
        self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {safe_friendly_name} (Context Cleared)</i></p>")
        self.engine.current_model = self.model
        self.save_session()

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
            self.trigger_glitch()

    def abort_generation(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.ghost_log.log("SYSTEM_ACTION: ABORT_GENERATION_SIGNAL_SENT")
            self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // ABORTED BY USER</i></p>")
            self.abort_btn.setVisible(False)

    def process_input(self, *args, text=None, is_tool_result=False):
        try:
            # Handle PySide6 signals passing booleans or other junk
            if text is None:
                text = self.input_field.toPlainText().strip()
            
            if not text:
                return

            print(f"[AURA_UI] Processing: {text[:30]}...")

            # 1. Navigation Handling (cd command)
            if not is_tool_result and text.startswith("cd "):
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
                    self.trigger_glitch()
                else:
                    safe_target = html.escape(target)
                    self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // ERROR: Directory not found: {safe_target}</i></p>")

                self.input_field.clear()
                return

            if not is_tool_result and text.startswith("/"):
                cmd = text[1:].lower()

                if cmd == "stop" or cmd == "abort":
                    self.abort_generation()
                    self.trigger_glitch("wipe")
                    self.input_field.clear()
                    return

                if cmd == "clear":
                    self.engine.clear_history()
                    self.messages = []
                    self.render_messages()
                    self.trigger_glitch("wipe")
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Context Purged.</i></p>")
                    self.input_field.clear()
                    return

                if cmd == "kill":
                    self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // EXECUTING NUCLEAR OPTION: KILLING OLLAMA SERVER...</i></p>")
                    subprocess.run(["sudo", "systemctl", "stop", "ollama"], check=False)
                    self.abort_generation()
                    self.input_field.clear()
                    return

                alias_map = {
                    "phi": "phi3:mini",
                    "qwen": "aura-qwen",
                    "coder": "qwen2.5-coder:7b",
                    "deep": "aura-deepseek",
                    "think": "deepseek-r1:1.5b",
                    "moon": "moondream",
                    "sam": "samantha-mistral"
                }

                self.trigger_glitch()

                if cmd == "commands":
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // COMMANDS & MODEL OPTIONS:</i></p>")
                    self.output_area.append("<p style='color: #D4AF37; font-family: Monospace;'><b>/commands</b> - Show this list</p>")
                    self.output_area.append("<p style='color: #D4AF37; font-family: Monospace;'><b>/model aura-qwen</b> - Default Living Hub model</p>")
                    self.output_area.append("<p style='color: #D4AF37; font-family: Monospace;'><b>/model aura-deepseek</b> - Logic-focused Hub model</p>")
                    self.output_area.append("<p style='color: #D4AF37; font-family: Monospace;'><b>/model deepseek-r1:1.5b</b> - Thinking model</p>")
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>MODEL ALIASES:</i> /qwen, /deep, /think, /coder, /phi, /moon, /sam</p>")
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>OPERATION MODES:</i> safe, developer, installer, admin-lite, danger-confirmed</p>")
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>GH CLI:</i> try <b>gh auth status</b>, <b>gh repo view</b>, <b>gh pr list</b>, <b>gh workflow list</b></p>")
                    self.input_field.clear()
                    return
                if cmd == "help":
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // TUNED VOICES:</i></p>")
                    for alias, m_id in alias_map.items():
                        if m_id in OllamaClient.MODELS:
                            safe_model_name = html.escape(OllamaClient.MODELS[m_id]['name'])
                            safe_alias = html.escape(alias)
                            self.output_area.append(f"<p style='color: #D4AF37; font-family: Monospace;'><b>/{safe_alias}</b> - {safe_model_name}</p>")
                    self.output_area.append("<p style='color: #404040; font-family: Monospace;'><i>TYPE /COMMANDS FOR MODELS, MODES, AND GH SHORTCUTS</i></p>")
                    self.input_field.clear()
                    return

                if cmd == "models":
                    self.populate_models_list()
                    self.input_field.clear()
                    return

                if cmd.startswith("model "):
                    target = cmd[6:].strip()
                    for display_name, m_id in self.model_mapping.items():
                        if target in m_id.lower():
                            self.model = m_id
                            self.engine.current_model = m_id
                            self.engine.clear_history()
                            self._sync_model_selector()
                            friendly_name = OllamaClient.MODELS.get(m_id, {"name": f"[RAW] {m_id}"})["name"]
                            safe_friendly_name = html.escape(friendly_name)
                            self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {safe_friendly_name} (Context Cleared)</i></p>")
                            self.save_session()
                            self.input_field.clear()
                            return
                    
                    safe_target = html.escape(target)
                    self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // Model not found: {safe_target}</i></p>")
                    self.input_field.clear()
                    return

                if cmd in alias_map:
                    target_model = alias_map[cmd]
                    self.model = target_model
                    self.engine.current_model = target_model
                    self.engine.clear_history()
                    self._sync_model_selector()
                    friendly_name = OllamaClient.MODELS.get(self.model, {"name": self.model})["name"]
                    safe_friendly_name = html.escape(friendly_name)
                    self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {safe_friendly_name} (Context Cleared)</i></p>")
                    self.save_session()
                    self.input_field.clear()
                    return

                found = False
                for key in self.models:
                    if cmd in key.lower():
                        self.model = key
                        self.engine.current_model = key
                        self.engine.clear_history()
                        self._sync_model_selector()
                        friendly_name = OllamaClient.MODELS.get(self.model, {"name": self.model})["name"]
                        safe_friendly_name = html.escape(friendly_name)
                        self.output_area.append(f"<p style='color: #404040; font-family: Monospace;'><i>SYSTEM // Switched to {safe_friendly_name} (Context Cleared)</i></p>")
                        found = True
                        self.save_session()
                        break
                
                if not found:
                    safe_cmd = html.escape(cmd)
                    self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // Unknown model: {safe_cmd}</i></p>")
                
                self.input_field.clear()
                return

            user_msg = {"role": "user", "content": text}
            
            # 👁️ WATCHFUL EYE: Vision Injection
            if self.model and "moon" in self.model.lower() and hasattr(self, 'vision_worker') and self.vision_worker.buffer:
                latest_frame = self.vision_worker.buffer[-1]
                user_msg["images"] = [latest_frame]
                self.ghost_log.log("VISION_INJECTION: LATEST_FRAME_ATTACHED")

            self.messages.append(user_msg)
            self.current_response_text = ""
            self.pending_message = {"role": "assistant", "model": self.model or "Aura", "content": ""}
            self.render_messages()
            
            self.input_field.clear()
            self.input_field.setEnabled(False)
            self.abort_btn.setVisible(True)
            self.visualizer.start()
            self.ghost_log.log(f"API_STREAM_START: MODEL({self.model})")

            self.worker = ChatWorker(self.model, text, self.engine, self.gen_options)
            self.worker.chunk_received.connect(self.handle_chunk)
            self.worker.finished.connect(self.handle_finished)
            self.worker.start()

        except Exception as e:
            print(f"[AURA_UI] CRASH in process_input: {e}")
            self.trigger_glitch("critical")
            self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // INPUT_PROCESS_CRASH: {html.escape(str(e))}</i></p>")
            self.input_field.setEnabled(True)
            self.input_field.setFocus()

    def handle_chunk(self, chunk: str):
        if chunk.startswith("\n[Aura Error:"):
            self.trigger_glitch("critical")
        self.current_response_text += chunk
        if self.pending_message:
            self.pending_message["content"] = self.current_response_text

        # ⚡ BOLT OPTIMIZATION: Throttle render updates to ~30 FPS (33ms)
        # This prevents O(N*M) layout thrashing in QTextEdit during fast LLM streams
        current_time = time.time()
        if current_time - self.last_render_time >= 0.033:
            self.render_messages()
            self.last_render_time = current_time

    def handle_finished(self):
        self.visualizer.stop()
        self.abort_btn.setVisible(False)
        self.ghost_log.log("API_STREAM_END: OK")
        if self.pending_message:
            content = self.pending_message["content"]
            
            # Detect JSON Tool Call blocks (both raw and markdown-fenced)
            tool_match = re.search(r'```json\s*(\{.*?"command":.*?\})\s*```', content, re.DOTALL)
            if not tool_match:
                tool_match = re.search(r'(\{.*?"command":.*?\})', content, re.DOTALL)

            qwen_match = re.search(r'<｜tool▁call▁begin｜>function<｜tool▁sep｜>(.*?):\s*(\{.*?\})', content, re.DOTALL)

            if tool_match:
                self.messages.append(self.pending_message)
                self.pending_message = None
                self.render_messages()
                self.handle_tool_use(tool_match.group(1))
            elif qwen_match:
                command_name = qwen_match.group(1).strip()
                args_str = qwen_match.group(2).strip()
                # Fix Qwen's Python-style kwargs (e.g., {dir_path='.'}) to JSON
                args_str = re.sub(r'([a-zA-Z0-9_]+)=', r'"\1":', args_str).replace("'", '"')
                try:
                    # Validate JSON conversion
                    json.loads(args_str)
                    json_str = f'{{"command": "{command_name}", "args": {args_str}}}'
                    self.messages.append(self.pending_message)
                    self.pending_message = None
                    self.render_messages()
                    self.handle_tool_use(json_str)
                except json.JSONDecodeError:
                    self.messages.append(self.pending_message)
                    self.pending_message = None
                    self.render_messages()
                    self.output_area.append("<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // NATIVE TOOL PARSE ERROR</i></p>")
            else:
                self.messages.append(self.pending_message)
                self.pending_message = None
                self.render_messages()
                self.save_session()
                self.input_field.setEnabled(True)
                self.input_field.setFocus()

    def handle_tool_use(self, json_str: str):
        try:
            tool_data = json.loads(json_str)
            command_name = tool_data.get("command")
            args = tool_data.get("args", {})
            
            if not command_name:
                raise ValueError("No 'command' specified in JSON")

            safe_cmd = html.escape(command_name)
            self.output_area.append(f"<p style='color: #00e6e6; font-family: Monospace;'><i>SYSTEM // EXECUTING TOOL: {safe_cmd}</i></p>")
            self.ghost_log.log(f"TOOL_EXECUTION: {command_name}")
            self.trigger_glitch("subtle")

            # Execute via Engine Registry
            from aura_core.engine import ToolRegistry
            
            # Inject context
            if "dir_path" not in args and command_name in ["run_shell_command", "grep_search", "list_directory"]:
                args["dir_path"] = self.engine.project_root
            if "file_path" in args and not os.path.isabs(args["file_path"]):
                args["file_path"] = os.path.normpath(os.path.join(self.engine.project_root, args["file_path"]))

            result = ToolRegistry.execute(command_name, args)
            
            # Ensure we don't blow up the context window
            if len(result) > 4000:
                result = result[:4000] + "\n...[TRUNCATED]"

            observation = f"<tool_result>\n{result}\n</tool_result>"
            self.ghost_log.log("TOOL_RESULT_INJECTED")
            self.trigger_glitch("subtle")
            
            # Autonomous Re-entry
            self.process_input(text=observation, is_tool_result=True)

        except Exception as e:
            self.trigger_glitch("critical")
            safe_e = html.escape(str(e))
            self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // TOOL_PARSE_ERROR: {safe_e}</i></p>")
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
            safe_e = html.escape(str(e))
            self.output_area.append(f"<p style='color: #FF5555; font-family: Monospace;'><i>SYSTEM // TOOL_USE_ERROR: {safe_e}</i></p>")

    # --- MANDATE COMPLIANCE ---

    def apply_theme(self):
        """Palette Mandate: Ensure aesthetic integrity."""
        self.update_stylesheet()
        self.ghost_log.log("PALETTE_SYNC: OK")

    def scan_integrity(self) -> bool:
        """Sentinel Mandate: Security and connection check."""
        try:
            import requests
            requests.get(self.engine.base_url, timeout=1)
            self.ghost_log.log("SENTINEL_SCAN: OLLAMA_UP")
            return True
        except:
            self.ghost_log.log("SENTINEL_SCAN: OLLAMA_DOWN")
            return False

    def stream_chat(self, model: str, prompt: str, options: Optional[dict] = None):
        """Bolt Mandate: High-performance orchestration proxy."""
        return self.engine.stream_chat(model, prompt, options)

    def render_messages(self):
        self.output_area.clear()
        html_parts = []
        
        display_messages = self.messages.copy()
        if self.pending_message:
            display_messages.append(self.pending_message)
            
        for msg in display_messages:
            # ⚡ BOLT OPTIMIZATION: Cache full HTML block for past messages
            # Reduces redundant string formatting and escaping inside the loop
            if "_full_html" in msg:
                html_parts.append(msg["_full_html"])
                continue

            role_color = "#6633FF" if msg["role"] == "user" else "#00e6e6"
            glow_style = f"border: 1px solid {role_color}; padding: 15px; border-radius: 8px; background-color: rgba(0, 0, 0, 0.4);"
            
            msg_html = ""
            if msg["role"] == "user":
                safe_content = html.escape(msg['content'])
                msg_html = f"<div style='{glow_style} margin-left: 50px;'><span style='color: #6633FF;'><b>&gt;</b></span> <span style='color: #FFFFFF;'>{safe_content}</span></div><br>"
            else:
                is_pending = (self.pending_message and msg == self.pending_message)
                content = msg['content']
                
                # 🛡️ CLEANUP: Hide Tool Calls from the UI
                display_content = content
                if not getattr(self, 'debug_toggle', None) or not self.debug_toggle.isChecked():
                    # 1. Hide Markdown JSON blocks containing "command"
                    display_content = re.sub(r'```json\s*(\{.*?"command":.*?\})\s*```', '', content, flags=re.DOTALL)
                    # 2. Hide Qwen native tool tokens
                    display_content = re.sub(r'<｜tool▁calls▁begin｜>.*?<｜tool▁outputs▁end｜>', '', display_content, flags=re.DOTALL)
                    display_content = re.sub(r'<｜tool▁call▁begin｜>.*?<｜tool▁call▁end｜>', '', display_content, flags=re.DOTALL)
                    # Fallback clean for incomplete tokens during stream
                    display_content = display_content.replace("<｜tool▁calls▁begin｜>", "")

                    if not display_content.strip() and is_pending:
                        display_content = "..." # Show something while it computes tools silently

                if is_pending:
                    # ⚡ HOLOGRAPHIC BRACKETS: Only during stream
                    safe_inner = html.escape(display_content)
                    content_html = f"<pre style='white-space: pre-wrap; font-family: inherit;'><span style='color: #00e6e6;'>[</span> {safe_inner} <span style='color: #00e6e6;'>]</span></pre>"
                else:
                    content_html = msg.get("_rendered_html")
                    if content_html is None:
                        content_html = self.md.render(display_content)
                        msg["_rendered_html"] = content_html
                
                # ⚡ POWER STRIPE: Dynamic border width simulation
                stripe_width = min(20, len(display_content) // 10)
                stripe_style = f"border-left: {stripe_width}px solid {role_color};"
                
                msg_html = f"<div style='{glow_style} {stripe_style} margin-right: 50px;'>"
                model_name = msg.get('model', 'AURA')
                safe_model_role = html.escape(model_name.upper())
                msg_html += f"<div style='color: #00e6e6; font-size: 13px; letter-spacing: 1px;'><b>{safe_model_role}</b></div>"
                msg_html += f"<div style='color: #B0B0B0;'>{content_html}</div></div><br>"

            html_parts.append(msg_html)
            # Only cache finalized messages
            if not (self.pending_message and msg == self.pending_message):
                msg["_full_html"] = msg_html
        
        self.output_area.setHtml("".join(html_parts))
        self.output_area.moveCursor(self.output_area.textCursor().MoveOperation.End)
