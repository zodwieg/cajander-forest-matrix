from qgis.core import QgsProcessingFeedback
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG


class ControllerLogBridge(QgsProcessingFeedback):
    """
    Потокобезопасный мост, перенаправляющий виртуальные методы QGIS
    в методы вашей вкладки LogTab.
    """

    def __init__(self, log_tab):
        super().__init__()
        self.log_tab = log_tab

    def pushConsoleInfo(self, info: str):
        # Используем встроенный в QWidget метод безопасного вызова,
        # чтобы текст добавлялся из фонового потока без вылетов
        self.log_tab.log_output.metaObject().invokeMethod(
            self.log_tab.log_output, "append", Qt.QueuedConnection, Q_ARG(str, info)
        )
        super().pushConsoleInfo(info)

    def setProgress(self, progress: float):
        self.log_tab.progress_bar.metaObject().invokeMethod(
            self.log_tab.progress_bar,
            "setValue",
            Qt.QueuedConnection,
            Q_ARG(int, int(progress)),
        )
        super().setProgress(progress)
