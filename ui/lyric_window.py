from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect

class LyricWindow(QWidget):
    def __init__(self, text: str, words: list, font_family: str, font_size: int, opacity: float, click_through: bool, inverted: bool = False, alignment_str: str = "justify", text_color: str = "#ffffff", bg_color: str = "#000000", parent: QWidget = None):
        super().__init__(parent)
        self.text = text
        self.words = words
        self.font_family = font_family
        self.font_size = font_size
        self.opacity = opacity
        self.inverted = inverted
        self.alignment_str = alignment_str
        self.text_color = text_color
        self.bg_color = bg_color
        
        # Frameless, transparent, always-on-top, tool window (no taskbar)
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        if click_through:
            flags |= Qt.WindowType.WindowTransparentForInput
        
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        self._init_ui()
        self.update_time(0)

    def _init_ui(self) -> None:
        # Layout for the top-level widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Margins to allow spacing
        
        # Frame representing the box
        self.frame = QFrame(self)
        
        # Parse hex background color
        bg_hex = self.text_color if self.inverted else self.bg_color
        color = QColor(bg_hex)
        rgba_val = f"rgba({color.red()}, {color.green()}, {color.blue()}, {int(self.opacity * 100)}%)"
        
        self.frame.setStyleSheet(f"QFrame {{ background-color: {rgba_val}; border-radius: 0px; }}")
        
        # Inner layout for padding
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(24, 24, 24, 24)
        
        # Text label
        self.label = QLabel(self.text, self.frame)
        self.label.setWordWrap(True)
        
        # Map alignment flag
        align_flag = Qt.AlignmentFlag.AlignCenter
        if self.alignment_str == "justify":
            align_flag = Qt.AlignmentFlag.AlignJustify | Qt.AlignmentFlag.AlignVCenter
        elif self.alignment_str == "left":
            align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif self.alignment_str == "right":
            align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
        self.label.setAlignment(align_flag)
        self.label.setStyleSheet("background: transparent;")
        
        # Apply font
        font = QFont(self.font_family, self.font_size)
        self.label.setFont(font)
        
        frame_layout.addWidget(self.label)
        layout.addWidget(self.frame)
        
        # Opacity effect for fade-in/fade-out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Adjust dimensions to wrap text properly
        self.adjust_size_to_text()

    def adjust_size_to_text(self) -> None:
        # Calculate dynamic size up to 420px max width to keep it compact and fill 4:3 vertical space
        font = QFont(self.font_family, self.font_size)
        metrics = self.label.fontMetrics()
        
        # Get width of single line of text plus padding
        text_width = metrics.horizontalAdvance(self.text)
        max_w = 420
        max_content_width = max_w - 48 - 20 # minus margins & padding
        
        if text_width < max_content_width:
            target_width = max(240, text_width + 48 + 20)  # Ensure minimum width to look good
        else:
            target_width = max_w
            
        self.setFixedWidth(target_width)
        self.setFixedHeight(target_width * 3 // 4) # Enforce 4:3 aspect ratio
        
        # Force layout recalculation
        self.layout().activate()

    def update_time(self, time_ms: int) -> None:
        if not self.words:
            return
        
        # Inverted mode swaps the background and text color.
        # Normal mode keeps custom text color and bg color as specified.
        visible_color = self.bg_color if self.inverted else self.text_color
        invisible_color = self.text_color if self.inverted else self.bg_color
        
        formatted = []
        for w in self.words:
            if time_ms < w.begin_ms:
                # Invisible: Color matches background so it occupies space but is hidden
                formatted.append(f"<span style='color: {invisible_color};'>{w.text}</span>")
            else:
                # Visible word
                formatted.append(f"<span style='color: {visible_color};'>{w.text}</span>")
        
        self.label.setText(" ".join(formatted))
