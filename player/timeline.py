from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QElapsedTimer

class Timeline(QObject):
    # Signals
    tick = pyqtSignal(int)          # Emits current playback time in ms
    state_changed = pyqtSignal(bool) # Emits True if playing, False if paused

    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._current_time_ms = 0
        self._duration_ms = 0
        self._speed = 1.0
        self._start_offset_ms = 0
        
        # High-resolution elapsed timer to compute delta time
        self._elapsed_timer = QElapsedTimer()
        
        # Tick timer for regular updates
        self._timer = QTimer(self)
        self._timer.setInterval(20)  # ~50 FPS ticks
        self._timer.timeout.connect(self._on_tick)

    def set_duration(self, duration_ms: int) -> None:
        self._duration_ms = duration_ms

    def duration(self) -> int:
        return self._duration_ms

    def set_speed(self, speed: float) -> None:
        self._speed = speed
        # If playing, shift offset basis to current time before resetting timer
        if self._is_playing:
            self._start_offset_ms = self._current_time_ms
            self._elapsed_timer.restart()

    def speed(self) -> float:
        return self._speed

    def current_time(self) -> int:
        return int(self._current_time_ms)

    def is_playing(self) -> bool:
        return self._is_playing

    def play(self) -> None:
        if not self._is_playing:
            self._is_playing = True
            self._start_offset_ms = self._current_time_ms
            self._elapsed_timer.start()
            self._timer.start()
            self.state_changed.emit(True)

    def pause(self) -> None:
        if self._is_playing:
            self._is_playing = False
            self._timer.stop()
            self._current_time_ms = self._start_offset_ms + self._elapsed_timer.elapsed()
            if self._current_time_ms > self._duration_ms:
                self._current_time_ms = self._duration_ms
            self.state_changed.emit(False)

    def stop(self) -> None:
        self.pause()
        self.seek(0)

    def seek(self, time_ms: int) -> None:
        was_playing = self._is_playing
        if was_playing:
            self.pause()
        self._current_time_ms = max(0, min(time_ms, self._duration_ms))
        self.tick.emit(int(self._current_time_ms))
        if was_playing:
            self.play()

    def _on_tick(self) -> None:
        if not self._is_playing:
            return
        
        # Use absolute elapsed time to prevent accumulation drift
        self._current_time_ms = self._start_offset_ms + self._elapsed_timer.elapsed()
        
        if self._current_time_ms >= self._duration_ms:
            self._current_time_ms = self._duration_ms
            self.pause()
            
        self.tick.emit(int(self._current_time_ms))
