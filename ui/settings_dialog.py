import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (QDialog, QFormLayout, QFontComboBox, QSpinBox, 
                             QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, QWidget,
                             QColorDialog, QLineEdit)
from config.config_manager import ConfigManager

class SettingsDialog(QDialog):
    def __init__(self, config_manager: ConfigManager, parent: QWidget = None):
        super().__init__(parent)
        self.config = config_manager
        
        self.setWindowTitle("Settings - Pyrics")
        self.resize(360, 540)
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #aaaaaa;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QFontComboBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                border: 0px;
                width: 10px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            #btn_apply {
                background-color: #ffffff;
                color: #000000;
                font-weight: bold;
                border: 1px solid #ffffff;
            }
            #btn_apply:hover {
                background-color: #e0e0e0;
            }
        """)
        
        self._init_ui()
        self._load_current_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Settings Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Font Selection
        self.cb_font = QFontComboBox(self)
        form_layout.addRow("Font Family:", self.cb_font)
        
        # Font Size
        self.sb_font_size = QSpinBox(self)
        self.sb_font_size.setRange(12, 100)
        form_layout.addRow("Font Size (px):", self.sb_font_size)
        
        # Window Opacity
        self.sb_opacity = QDoubleSpinBox(self)
        self.sb_opacity.setRange(0.1, 1.0)
        self.sb_opacity.setSingleStep(0.05)
        form_layout.addRow("Window Opacity:", self.sb_opacity)
        
        # Animation Duration
        self.sb_duration = QDoubleSpinBox(self)
        self.sb_duration.setRange(2.0, 60.0)
        self.sb_duration.setSingleStep(0.5)
        form_layout.addRow("Duration (sec):", self.sb_duration)
        
        # Side Spacing
        self.sb_side_spacing = QSpinBox(self)
        self.sb_side_spacing.setRange(10, 400)
        form_layout.addRow("Side Spacing (px):", self.sb_side_spacing)
        
        # Click Through checkbox
        self.chk_click_through = QCheckBox("Enable Click-Through", self)
        form_layout.addRow("", self.chk_click_through)
        
        # Color Theme Dropdown
        self.cb_theme = QComboBox(self)
        self.cb_theme.addItems(["Random Mix", "Force Normal", "Force Inverted"])
        form_layout.addRow("Theme Style:", self.cb_theme)
        
        # Text Justify alignment
        self.cb_align = QComboBox(self)
        self.cb_align.addItems(["Justified", "Centered", "Left", "Right"])
        form_layout.addRow("Text Alignment:", self.cb_align)
        
        # Text Color Customization
        text_color_layout = QHBoxLayout()
        self.txt_text_color = QLineEdit(self)
        self.txt_text_color.setPlaceholderText("#ffffff")
        self.btn_pick_text_color = QPushButton("Choose...", self)
        text_color_layout.addWidget(self.txt_text_color)
        text_color_layout.addWidget(self.btn_pick_text_color)
        form_layout.addRow("Text Color (Hex):", text_color_layout)
        
        # BG Color Customization
        bg_color_layout = QHBoxLayout()
        self.txt_bg_color = QLineEdit(self)
        self.txt_bg_color.setPlaceholderText("#000000")
        self.btn_pick_bg_color = QPushButton("Choose...", self)
        bg_color_layout.addWidget(self.txt_bg_color)
        bg_color_layout.addWidget(self.btn_pick_bg_color)
        form_layout.addRow("BG Color (Hex):", bg_color_layout)
        
        layout.addLayout(form_layout)
        
        # Import/Export configuration buttons
        import_export_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import Config", self)
        self.btn_export = QPushButton("Export Config", self)
        import_export_layout.addWidget(self.btn_import)
        import_export_layout.addWidget(self.btn_export)
        layout.addLayout(import_export_layout)
        
        # Line break
        line = QWidget(self)
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #333333;")
        layout.addWidget(line)
        
        # Action Buttons (Apply, Reset Defaults, Close)
        actions_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Apply", self)
        self.btn_apply.setObjectName("btn_apply")
        self.btn_reset = QPushButton("Reset Defaults", self)
        self.btn_close = QPushButton("Close", self)
        actions_layout.addWidget(self.btn_close)
        actions_layout.addWidget(self.btn_reset)
        actions_layout.addWidget(self.btn_apply)
        layout.addLayout(actions_layout)
        
        # License/Author credit
        self.lbl_license = QLabel("MIT Licensed - Made by abdipr", self)
        self.lbl_license.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_license.setStyleSheet("font-size: 10px; color: #555555; margin-top: 4px;")
        layout.addWidget(self.lbl_license)
        
        # Connect Actions
        self.btn_apply.clicked.connect(self._apply_settings)
        self.btn_reset.clicked.connect(self._reset_defaults)
        self.btn_close.clicked.connect(self.reject)
        self.btn_import.clicked.connect(self._import_config)
        self.btn_export.clicked.connect(self._export_config)
        self.btn_pick_text_color.clicked.connect(self._pick_text_color)
        self.btn_pick_bg_color.clicked.connect(self._pick_bg_color)

    def _load_current_settings(self) -> None:
        font_sz = int(self.config.get("font_size"))
        self.cb_font.setCurrentFont(QFont(self.config.get("font_family"), font_sz))
        self.sb_font_size.setValue(int(self.config.get("font_size")))
        self.sb_opacity.setValue(float(self.config.get("window_opacity")))
        self.sb_duration.setValue(float(self.config.get("animation_duration_s")))
        self.sb_side_spacing.setValue(int(self.config.get("side_spacing")))
        self.chk_click_through.setChecked(bool(self.config.get("click_through")))
        self.txt_text_color.setText(str(self.config.get("text_color")))
        self.txt_bg_color.setText(str(self.config.get("bg_color")))
        
        # Map theme value
        theme = self.config.get("theme")
        theme_index = 0
        if theme == "normal":
            theme_index = 1
        elif theme == "inverted":
            theme_index = 2
        self.cb_theme.setCurrentIndex(theme_index)
        
        # Map text align
        align = self.config.get("text_align")
        align_index = 0
        if align == "center":
            align_index = 1
        elif align == "left":
            align_index = 2
        elif align == "right":
            align_index = 3
        self.cb_align.setCurrentIndex(align_index)

    def _apply_settings(self) -> None:
        # Save values to config manager
        self.config.set("font_family", self.cb_font.currentFont().family())
        self.config.set("font_size", self.sb_font_size.value())
        self.config.set("window_opacity", self.sb_opacity.value())
        self.config.set("animation_duration_s", self.sb_duration.value())
        self.config.set("side_spacing", self.sb_side_spacing.value())
        self.config.set("click_through", self.chk_click_through.isChecked())
        
        # Save text and bg colors (with fallback if empty)
        txt_col = self.txt_text_color.text().strip() or "#ffffff"
        bg_col = self.txt_bg_color.text().strip() or "#000000"
        self.config.set("text_color", txt_col)
        self.config.set("bg_color", bg_col)
        
        # Save theme value
        theme_val = "random"
        if self.cb_theme.currentIndex() == 1:
            theme_val = "normal"
        elif self.cb_theme.currentIndex() == 2:
            theme_val = "inverted"
        self.config.set("theme", theme_val)
        
        # Save text align
        align_val = "justify"
        if self.cb_align.currentIndex() == 1:
            align_val = "center"
        elif self.cb_align.currentIndex() == 2:
            align_val = "left"
        elif self.cb_align.currentIndex() == 3:
            align_val = "right"
        self.config.set("text_align", align_val)
        
        self.config.save()
        self.accept()

    def _reset_defaults(self) -> None:
        self.config.reset_to_defaults()
        self._load_current_settings()

    def _pick_text_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.txt_text_color.text() or "#ffffff"), self, "Choose Text Color")
        if color.isValid():
            self.txt_text_color.setText(color.name())
            
    def _pick_bg_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.txt_bg_color.text() or "#000000"), self, "Choose BG Color")
        if color.isValid():
            self.txt_bg_color.setText(color.name())

    def _import_config(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Config File", "", "JSON Files (*.json)"
        )
        if file_path:
            if self.config.load_from_path(file_path):
                self._load_current_settings()
                # Apply loaded settings immediately
                self._apply_settings()

    def _export_config(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Config File", "custom_config.json", "JSON Files (*.json)"
        )
        if file_path:
            # First collect current UI values
            theme_val = "random"
            if self.cb_theme.currentIndex() == 1:
                theme_val = "normal"
            elif self.cb_theme.currentIndex() == 2:
                theme_val = "inverted"
                
            align_val = "justify"
            if self.cb_align.currentIndex() == 1:
                align_val = "center"
            elif self.cb_align.currentIndex() == 2:
                align_val = "left"
            elif self.cb_align.currentIndex() == 3:
                align_val = "right"
                
            self.config.set("font_family", self.cb_font.currentFont().family())
            self.config.set("font_size", self.sb_font_size.value())
            self.config.set("window_opacity", self.sb_opacity.value())
            self.config.set("animation_duration_s", self.sb_duration.value())
            self.config.set("side_spacing", self.sb_side_spacing.value())
            self.config.set("click_through", self.chk_click_through.isChecked())
            self.config.set("theme", theme_val)
            self.config.set("text_align", align_val)
            self.config.set("text_color", self.txt_text_color.text().strip() or "#ffffff")
            self.config.set("bg_color", self.txt_bg_color.text().strip() or "#000000")
            
            # Save to target path
            if self.config.save_to_path(file_path):
                print(f"Config successfully exported to {file_path}")
