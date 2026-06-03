import os
import json
from typing import Any, Dict
from PyQt6.QtCore import QObject, pyqtSignal

DEFAULT_CONFIG = {
    "font_family": "Arial Narrow",
    "font_size": 32,
    "window_opacity": 1.0,
    "animation_duration_s": 12.0,
    "side_spacing": 80,
    "random_offset_range": 50,
    "playback_speed": 1.0,
    "click_through": False,
    "theme": "random",         # Options: "random", "normal", "inverted"
    "text_align": "justify",     # Options: "justify", "center", "left", "right"
    "text_color": "#ffffff",
    "bg_color": "#000000"
}

class ConfigManager(QObject):
    settings_changed = pyqtSignal()

    def __init__(self, config_path: str = "config.json"):
        super().__init__()
        self.config_path = config_path
        self.settings: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def reset_to_defaults(self) -> None:
        self.settings = DEFAULT_CONFIG.copy()
        self.save()

    def load(self) -> None:
        self.load_from_path(self.config_path)

    def load_from_path(self, path: str) -> bool:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in DEFAULT_CONFIG.items():
                        self.settings[k] = data.get(k, v)
                self.settings_changed.emit()
                return True
            except Exception as e:
                print(f"Error loading config from {path}: {e}")
        return False

    def save(self) -> None:
        if self.save_to_path(self.config_path):
            self.settings_changed.emit()

    def save_to_path(self, path: str) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config to {path}: {e}")
        return False

    def get(self, key: str) -> Any:
        return self.settings.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any) -> None:
        if key in DEFAULT_CONFIG:
            self.settings[key] = value
            self.save()
