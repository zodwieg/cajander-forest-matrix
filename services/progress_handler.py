# services/progress_handler.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import QgsProcessingFeedback


def create_processing_progress(
    parent_window, message: str
) -> tuple[QProgressDialog, QgsProcessingFeedback]:
    """
    Фабрика для создания пары: Диалог прогресса + Фидбек QGIS.
    Сокращает бойлерплейт в контроллерах.
    """
    feedback = QgsProcessingFeedback()

    progress_dialog = QProgressDialog(message, "Отмена", 0, 0, parent_window)
    progress_dialog.setWindowTitle("Расчет")
    progress_dialog.setWindowModality(Qt.WindowModal)

    # Привязываем изменение прогресса к UI
    feedback.progressChanged.connect(
        lambda progress: (
            progress_dialog.setValue(int(progress)) if progress > 0 else None
        )
    )
    # Привязываем кнопку Отмена к фидбеку алгоритма
    progress_dialog.canceled.connect(feedback.cancel)

    return progress_dialog, feedback
