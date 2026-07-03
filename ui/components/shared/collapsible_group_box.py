from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt


class CollapsibleGroupBox(QGroupBox):
    """
    Сворачиваемая группа на базе стандартного QGroupBox.
    Заголовок стабильно рендерится системой строго по центру рамки.
    """

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._raw_title = title
        self._is_collapsed = False

        # Минималистичный стиль для предсказуемого отображения на любой ОС
        self.setStyleSheet("""
            CollapsibleGroupBox { 
                font-weight: bold; 
                margin-top: 10px; 
            }
            CollapsibleGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                left: 10px;
                padding: 0 3px;
            }
        """)

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        # Отступ сверху побольше, чтобы контент не перекрывал системный заголовок
        self.content_layout.setContentsMargins(10, 15, 10, 10)
        self.content_layout.setSpacing(10)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_widget)

        self._update_title()

    def mousePressEvent(self, event):
        # Клик обрабатывается строго в верхней зоне заголовка
        if event.pos().y() < 25 and event.button() == Qt.LeftButton:
            self.toggle_collapsed()
        else:
            super().mousePressEvent(event)

    def toggle_collapsed(self):
        self._is_collapsed = not self._is_collapsed
        self.content_widget.setVisible(not self._is_collapsed)
        self._update_title()

    def _update_title(self):
        arrow = "▼" if not self._is_collapsed else "►"
        super().setTitle(f"{arrow} {self._raw_title}")
