import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QFileDialog, QComboBox)
from config.config_manager import ConfigManager
from player.timeline import Timeline

class ControlPanel(QWidget):
    # Signals
    file_loaded = pyqtSignal(str)  # Emits the selected file path

    def __init__(self, timeline: Timeline, config_manager: ConfigManager):
        super().__init__()
        self.timeline = timeline
        self.config = config_manager
        self._is_slider_pressed = False
        
        self.setWindowTitle("Python Lyrics Player")
        self.resize(440, 130)
        # Remove maximize button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 4px 10px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                height: 5px;
                background: #1e1e1e;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #333333;
                width: 12px;
                height: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 6px;
            }
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 3px 6px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #333333;
            }
            QLabel {
                color: #aaaaaa;
            }
        """)
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(10, 10, 10, 8)
        
        # File selector row
        file_layout = QHBoxLayout()
        self.btn_open = QPushButton("Open File", self)
        self.lbl_file = QLabel("No file loaded", self)
        self.lbl_file.setWordWrap(False)
        file_layout.addWidget(self.btn_open)
        file_layout.addWidget(self.lbl_file, 1)
        main_layout.addLayout(file_layout)
        
        # Timeline progress slider & labels
        slider_layout = QHBoxLayout()
        self.lbl_current_time = QLabel("00:00", self)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 1000)
        self.slider.setEnabled(False)
        self.lbl_total_duration = QLabel("00:00", self)
        
        slider_layout.addWidget(self.lbl_current_time)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.lbl_total_duration)
        main_layout.addLayout(slider_layout)
        
        # Controls row (Play/Pause, Stop, Restart, Settings, Playback Speed)
        ctrl_layout = QHBoxLayout()
        
        self.btn_play_pause = QPushButton("Play", self)
        self.btn_stop = QPushButton("Stop", self)
        self.btn_restart = QPushButton("Restart", self)
        self.btn_settings = QPushButton("Settings", self)
        
        self.btn_play_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_restart.setEnabled(False)
        
        ctrl_layout.addWidget(self.btn_play_pause)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addWidget(self.btn_restart)
        ctrl_layout.addWidget(self.btn_settings)
        ctrl_layout.addSpacing(10)
        
        # Speed dropdown
        ctrl_layout.addWidget(QLabel("Speed:", self))
        self.cb_speed = QComboBox(self)
        self.cb_speed.addItems(["0.5x", "1x", "1.25x", "1.5x", "2x"])
        self.cb_speed.setCurrentText("1x")
        ctrl_layout.addWidget(self.cb_speed)
        
        main_layout.addLayout(ctrl_layout)

    def _connect_signals(self) -> None:
        self.btn_open.clicked.connect(self._open_file_dialog)
        
        # Playback control bindings
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        self.btn_stop.clicked.connect(self.timeline.stop)
        self.btn_restart.clicked.connect(lambda: self.timeline.seek(0) or self.timeline.play())
        
        # Speed binding
        self.cb_speed.currentTextChanged.connect(self._on_speed_changed)
        
        # Slider connections to handle seeking properly
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.slider.valueChanged.connect(self._on_slider_value_changed)
        
        # Timeline connections
        self.timeline.tick.connect(self._on_timeline_tick)
        self.timeline.state_changed.connect(self._on_timeline_state_changed)
        
        # Settings connection
        self.btn_settings.clicked.connect(self._open_settings)

    def _open_settings(self) -> None:
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        dialog.exec()

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open TTML Lyrics File", "", "TTML Files (*.ttml);;XML Files (*.xml);;All Files (*)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            display_name = filename
            if len(filename) > 30:
                display_name = filename[:27] + "..."
            self.lbl_file.setText(display_name)
            self.file_loaded.emit(file_path)
            
            # Enable buttons once loaded
            self.btn_play_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_restart.setEnabled(True)
            self.slider.setEnabled(True)

    def _toggle_play_pause(self) -> None:
        if self.timeline.is_playing():
            self.timeline.pause()
        else:
            self.timeline.play()

    def _on_speed_changed(self, speed_text: str) -> None:
        speed = float(speed_text.replace("x", ""))
        self.timeline.set_speed(speed)

    def _on_slider_pressed(self) -> None:
        self._is_slider_pressed = True

    def _on_slider_released(self) -> None:
        self._is_slider_pressed = False
        duration = self.timeline.duration()
        if duration > 0:
            target_ms = int((self.slider.value() / 1000.0) * duration)
            self.timeline.seek(target_ms)

    def _on_slider_value_changed(self, value: int) -> None:
        if self._is_slider_pressed:
            # Update the time label live while scrubbing
            duration = self.timeline.duration()
            current_ms = int((value / 1000.0) * duration)
            self.lbl_current_time.setText(self.format_time(current_ms))

    def _on_timeline_tick(self, time_ms: int) -> None:
        if not self._is_slider_pressed:
            duration = self.timeline.duration()
            if duration > 0:
                val = int((time_ms / duration) * 1000)
                self.slider.blockSignals(True)
                self.slider.setValue(val)
                self.slider.blockSignals(False)
            self.lbl_current_time.setText(self.format_time(time_ms))

    def _on_timeline_state_changed(self, is_playing: bool) -> None:
        if is_playing:
            self.btn_play_pause.setText("Pause")
            self.btn_play_pause.setStyleSheet("QPushButton { font-weight: bold; background-color: #333333; }")
        else:
            self.btn_play_pause.setText("Play")
            self.btn_play_pause.setStyleSheet("")

    def update_duration_display(self, duration_ms: int) -> None:
        self.lbl_total_duration.setText(self.format_time(duration_ms))
        self.lbl_current_time.setText("00:00")
        self.slider.setValue(0)

    @staticmethod
    def format_time(ms: int) -> str:
        s = ms // 1000
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"
