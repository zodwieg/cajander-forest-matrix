from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QProgressBar
from PyQt5.QtCore import pyqtSlot
from qgis.core import QgsProcessingFeedback


class LogTab(QWidget):
    """Компонент для отображения хода выполнения тяжелых задач"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Стандартное текстовое поле для логов
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Прогресс-бар прямо внутри вкладки лога (или под ней)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

    def prepare_for_run(self):
        """Сброс состояния перед новым запуском"""
        self.log_output.clear()
        self.progress_bar.setRange(0, 0)  # Режим "бегунка" до первых данных
        self.progress_bar.setVisible(True)

    def finish_run(self):
        """Скрытие элементов после завершения"""
        self.progress_bar.setVisible(False)

    @pyqtSlot(str)
    def append_text(self, text: str):
        self.log_output.append(text)
        self.log_output.ensureCursorVisible()

    @pyqtSlot(float)
    def set_progress(self, progress: float):
        if self.progress_bar.minimum() == 0 and self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(progress))
