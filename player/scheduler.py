from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
from parser.ttml_parser import LyricLine
from player.timeline import Timeline

class Scheduler(QObject):
    # Signals
    spawn_lyric = pyqtSignal(LyricLine)  # Emitted when a lyric line is scheduled to start
    clear_lyrics = pyqtSignal()          # Emitted when lyrics need to be cleared (e.g. seek / stop)

    def __init__(self, timeline: Timeline):
        super().__init__()
        self.timeline = timeline
        self.lyrics: List[LyricLine] = []
        self._next_index = 0
        
        # Connect timeline tick
        self.timeline.tick.connect(self._on_tick)

    def set_lyrics(self, lyrics: List[LyricLine]) -> None:
        self.lyrics = lyrics
        self.reset()
        if lyrics:
            # Set timeline duration to the end of the last lyric line + buffer
            last_end = lyrics[-1].end_ms
            self.timeline.set_duration(last_end + 5000) # 5 seconds extra
        else:
            self.timeline.set_duration(0)

    def reset(self) -> None:
        self._next_index = 0
        self.clear_lyrics.emit()

    def seek_to_time(self, time_ms: int) -> None:
        # Clear currently active visual lyrics
        self.clear_lyrics.emit()
        
        # Find the first lyric that begins at or after time_ms (considering early spawn offset of 3s)
        self._next_index = 0
        for i, lyric in enumerate(self.lyrics):
            if lyric.begin_ms - 3000 >= time_ms:
                self._next_index = i
                break
            else:
                self._next_index = i + 1

    def _on_tick(self, current_time_ms: int) -> None:
        # Check if we have lyrics to process
        while self._next_index < len(self.lyrics):
            lyric = self.lyrics[self._next_index]
            # Spawn 3 seconds ahead of the lyric begin timestamp
            if current_time_ms >= lyric.begin_ms - 3000:
                # Trigger spawn
                self.spawn_lyric.emit(lyric)
                self._next_index += 1
            else:
                break
