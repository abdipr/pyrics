import random
import time
from typing import Dict, List, Tuple
from PyQt6.QtGui import QGuiApplication, QFont, QColor
from PyQt6.QtCore import QObject, Qt, QPoint, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QTimer, QElapsedTimer
from PyQt6.QtWidgets import QWidget
from config.config_manager import ConfigManager
from parser.ttml_parser import LyricLine
from player.timeline import Timeline
from ui.lyric_window import LyricWindow

class AnimationManager(QObject):
    def __init__(self, config_manager: ConfigManager, control_panel: QWidget, timeline: Timeline):
        super().__init__()
        self.config = config_manager
        self.control_panel = control_panel
        self.timeline = timeline
        self.is_paused = False
        
        # List of active lyric entries
        # Entry: { "window": LyricWindow, "side": str, "x": float, "y": float, "start_y": float, "end_y": float }
        self.active_lyrics: List[dict] = []
        self.last_side = "RIGHT"  # Start with LEFT next
        
        # Track last spawned details per side to prevent overlaps
        self.last_spawn_info: Dict[str, Tuple[float, float, float]] = {}

        # High-resolution delta timer for 60 FPS movement
        self.frame_timer = QTimer(self)
        self.frame_timer.setInterval(16)  # ~60 FPS
        self.frame_timer.timeout.connect(self._update_positions)
        
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

    def set_paused(self, paused: bool) -> None:
        self.is_paused = paused
        if paused:
            self.frame_timer.stop()
        else:
            self.elapsed_timer.restart()
            self.frame_timer.start()

    def clear(self) -> None:
        self.frame_timer.stop()
        for entry in self.active_lyrics:
            try:
                entry["window"].close()
            except Exception:
                pass
        self.active_lyrics.clear()
        self.last_spawn_info.clear()
        self.last_side = "RIGHT"

    def spawn_lyric(self, lyric: LyricLine) -> None:
        # Get configuration settings
        font_family = self.config.get("font_family")
        font_size = self.config.get("font_size")
        opacity = self.config.get("window_opacity")
        duration_s = self.config.get("animation_duration_s")
        side_spacing = self.config.get("side_spacing")
        random_offset_range = self.config.get("random_offset_range")
        click_through = self.config.get("click_through")
        theme = self.config.get("theme")
        alignment_str = self.config.get("text_align")
        text_color = self.config.get("text_color")
        bg_color = self.config.get("bg_color")
        
        # Determine screen
        screen = QGuiApplication.screenAt(self.control_panel.pos()) or QGuiApplication.primaryScreen()
        if not screen:
            return
        
        screen_geom = screen.geometry()
        screen_w = screen_geom.width()
        screen_h = screen_geom.height()
        screen_x = screen_geom.x()
        screen_y = screen_geom.y()
        
        # Determine inverted state
        if theme == "normal":
            inverted = False
        elif theme == "inverted":
            inverted = True
        else:
            inverted = random.random() < 0.3
            
        # Create lyric window
        window = LyricWindow(lyric.text, lyric.words, font_family, font_size, opacity, click_through, inverted, alignment_str, text_color, bg_color)
        
        # Connect timeline tick to update word-by-word state
        self.timeline.tick.connect(window.update_time)
        window.update_time(self.timeline.current_time())
        
        # Alternate sides
        side = "LEFT" if self.last_side == "RIGHT" else "RIGHT"
        self.last_side = side
        
        # Calculate random offset
        offset = random.randint(-random_offset_range, random_offset_range)
        
        # Calculate X coordinate
        if side == "LEFT":
            x = screen_x + side_spacing + offset
        else:
            x = screen_x + screen_w - window.width() - side_spacing + offset
        x = max(screen_x + 10, min(x, screen_x + screen_w - window.width() - 10))
        
        # Default start and end Y
        default_spawn_y = screen_y + screen_h + 50
        end_y = screen_y - window.height() - 50
        
        # Dynamic distance
        spawn_y = default_spawn_y
        now = time.time()
        
        # Constant base velocity (distance over base duration)
        default_distance = default_spawn_y - end_y
        base_velocity = default_distance / duration_s
        
        # Smart Stacking: Check for overlap on the same side using real-time speed
        current_speed = self.timeline.speed()
        velocity = base_velocity * current_speed
        
        if side in self.last_spawn_info:
            last_time, last_spawn_y, last_height = self.last_spawn_info[side]
            elapsed = now - last_time
            last_current_y = last_spawn_y - (velocity * elapsed)
            
            collision_threshold = last_current_y + last_height + 40
            if spawn_y < collision_threshold:
                spawn_y = collision_threshold
        
        # Save spawn info
        self.last_spawn_info[side] = (now, spawn_y, window.height())
        
        # Move and display window
        window.move(int(x), int(spawn_y))
        window.show()
        
        # Add to tracking list
        self.active_lyrics.append({
            "window": window,
            "side": side,
            "x": float(x),
            "y": float(spawn_y),
            "start_y": float(spawn_y),
            "end_y": float(end_y)
        })
        
        # Start frame updates if not running and not paused
        if not self.is_paused and not self.frame_timer.isActive():
            self.elapsed_timer.restart()
            self.frame_timer.start()

    def _update_positions(self) -> None:
        if not self.active_lyrics:
            self.frame_timer.stop()
            return
            
        dt = self.elapsed_timer.restart() / 1000.0  # seconds elapsed
        
        # Get live config parameters for on-the-fly settings updating
        duration_s = self.config.get("animation_duration_s")
        current_speed = self.timeline.speed()
        
        remaining = []
        for entry in self.active_lyrics:
            window = entry["window"]
            
            # Calculate dynamic velocity based on live speed and duration settings
            default_distance = entry["start_y"] - entry["end_y"]
            base_velocity = default_distance / duration_s
            velocity = base_velocity * current_speed
            
            # Move Y position
            entry["y"] -= velocity * dt
            
            # Close window if it passes the destination
            if entry["y"] <= entry["end_y"]:
                try:
                    window.close()
                except Exception:
                    pass
                continue
                
            # Apply position update
            window.move(int(entry["x"]), int(entry["y"]))
            
            # Calculate completion ratio for custom opacity curves
            total_dist = entry["start_y"] - entry["end_y"]
            current_dist = entry["start_y"] - entry["y"]
            ratio = current_dist / total_dist if total_dist > 0 else 1.0
            
            # Smooth fade in (first 10%) & fade out (last 15%)
            if ratio < 0.10:
                fade_opacity = ratio / 0.10
            elif ratio > 0.85:
                fade_opacity = (1.0 - ratio) / 0.15
            else:
                fade_opacity = 1.0
                
            # Apply overall opacity
            window.opacity_effect.setOpacity(fade_opacity)
            remaining.append(entry)
            
        self.active_lyrics = remaining

    def refresh_settings(self) -> None:
        font_family = self.config.get("font_family")
        font_size = self.config.get("font_size")
        opacity = self.config.get("window_opacity")
        click_through = self.config.get("click_through")
        text_color = self.config.get("text_color")
        bg_color = self.config.get("bg_color")
        alignment_str = self.config.get("text_align")
        
        for entry in self.active_lyrics:
            window = entry["window"]
            
            flags = window.windowFlags()
            if click_through:
                flags |= Qt.WindowType.WindowTransparentForInput
            else:
                flags &= ~Qt.WindowType.WindowTransparentForInput
            
            if flags != window.windowFlags():
                window.setWindowFlags(flags)
                window.show()
                
            window.font_family = font_family
            window.font_size = font_size
            window.opacity = opacity
            window.text_color = text_color
            window.bg_color = bg_color
            window.alignment_str = alignment_str
            
            bg_hex = window.text_color if window.inverted else window.bg_color
            color = QColor(bg_hex)
            rgba_val = f"rgba({color.red()}, {color.green()}, {color.blue()}, {int(opacity * 100)}%)"
            window.frame.setStyleSheet(f"QFrame {{ background-color: {rgba_val}; border-radius: 0px; }}")
            
            font = QFont(font_family, font_size)
            window.label.setFont(font)
            
            align_flag = Qt.AlignmentFlag.AlignCenter
            if alignment_str == "justify":
                align_flag = Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter
            elif alignment_str == "left":
                align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            elif alignment_str == "right":
                align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            window.label.setAlignment(align_flag)
            
            window.adjust_size_to_text()
            window.update_time(self.timeline.current_time())
