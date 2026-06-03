import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon
from config.config_manager import ConfigManager
from parser.ttml_parser import parse_ttml
from player.timeline import Timeline
from player.scheduler import Scheduler
from ui.control_panel import ControlPanel
from ui.animation_manager import AnimationManager

def get_resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_custom_fonts() -> None:
    # Look for fonts in get_resource_path
    fonts_dir = get_resource_path("fonts")
    if not os.path.exists(fonts_dir):
        return

    for filename in os.listdir(fonts_dir):
        if filename.lower().endswith((".ttf", ".otf")):
            path = os.path.join(fonts_dir, filename)
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font family: {families}")
            else:
                print(f"Failed to load font: {filename}")

def main() -> None:
    # Explicitly set AppUserModelID on Windows for the taskbar icon to show up correctly
    try:
        import ctypes
        myappid = 'abdipr.pyrics.lyricplayer.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
        
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Pyrics - Python Lyrics Player")
    app.setApplicationDisplayName("Pyrics")
    
    # Set Application Icon
    icon_path = get_resource_path(os.path.join("favicon", "favicon.ico"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Icon not found at: {icon_path}")
    
    # Load fonts
    load_custom_fonts()
    
    # Initialize Core Settings and Components (config.json is kept in cwd for write access)
    config_manager = ConfigManager(config_path="config.json")
    timeline = Timeline()
    scheduler = Scheduler(timeline)
    
    # Create Control Panel
    control_panel = ControlPanel(timeline, config_manager)
    
    # Create Animation Manager
    animation_manager = AnimationManager(config_manager, control_panel, timeline)
    
    # Wire settings updates to immediately refresh floaters
    config_manager.settings_changed.connect(animation_manager.refresh_settings)
    
    # Wire events
    def on_file_loaded(file_path: str) -> None:
        lyrics = parse_ttml(file_path)
        scheduler.set_lyrics(lyrics)
        control_panel.update_duration_display(timeline.duration())
        print(f"Loaded {len(lyrics)} lyric lines from {file_path}")

    control_panel.file_loaded.connect(on_file_loaded)
    
    # When timeline state changes (play/pause), pause or resume animations
    timeline.state_changed.connect(lambda is_playing: animation_manager.set_paused(not is_playing))
    
    # When timeline seeks, update the scheduler
    timeline.tick.connect(lambda time_ms: None) # placeholder to ensure connections work
    
    # Seek binding to clear and reset index
    control_panel.slider.sliderReleased.connect(
        lambda: scheduler.seek_to_time(timeline.current_time())
    )
    
    # When stopping or resetting, clear windows
    scheduler.clear_lyrics.connect(animation_manager.clear)
    
    # Spawn lyric window on event trigger
    scheduler.spawn_lyric.connect(animation_manager.spawn_lyric)
    
    # Display Control Panel
    control_panel.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
