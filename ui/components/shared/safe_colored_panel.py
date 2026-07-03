from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor


class SafeColoredPanel(QWidget):
    """Виджет-подложка, который красит себя сам через QPainter,
    вообще не используя QSS и не ломая нативные стили формы."""

    def __init__(self, bg_hex_color, parent=None):
        super().__init__(parent)
        hex_color = bg_hex_color if bg_hex_color.startswith("#") else f"#{bg_hex_color}"
        self.bg_color = QColor(hex_color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Задаем легкую прозрачную рамку (аналог 1px solid rgba(0,0,0,0.06))
        painter.setPen(QColor(0, 0, 0, 15))
        # Задаем цвет заливки
        painter.setBrush(self.bg_color)

        # Рисуем скругленный прямоугольник (6px скругление углов)
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 6.0, 6.0)
