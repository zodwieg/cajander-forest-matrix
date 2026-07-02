import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication, QgsProcessingProvider

from .cajander_processing_tool import CajanderMatrixAlgorithm
from .config import constants as c

# Импортируем наш новый контроллер вместо диалога напрямую
from .controllers.calibration_controller import CalibrationController


class CajanderMatrixProvider(QgsProcessingProvider):
    """Провайдер, который регистрирует наши инструменты в панели Processing."""

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(CajanderMatrixAlgorithm())

    def id(self):
        return c.PROVIDER_NAME

    def name(self):
        return "Матрица Каяндера"

    def icon(self):
        return QIcon()


class CajanderPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None

        # Ссылка на контроллер калибровки (Lazy Load внутри)
        self.calibration_controller = None
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        # 1. Регистрация провайдера
        self.provider = CajanderMatrixProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        # 2. Подготовка иконки
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = (
            QIcon(icon_path)
            if os.path.exists(icon_path)
            else QIcon(QgsApplication.reportStyleSheet())
        )

        # 3. Создаем экшен
        self.action = QAction(
            icon, "Калибровка алгоритма биомов...", self.iface.mainWindow()
        )

        # Изменяем привязку: теперь клик вызывает метод инициализации контроллера
        self.action.triggered.connect(self.run_calibration)

        # Добавляем в интерфейс QGIS
        self.iface.addPluginToRasterMenu("Матрица Каяндера", self.action)
        self.iface.addRasterToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removeRasterToolBarIcon(self.action)
            self.iface.removePluginRasterMenu("Матрица Каяндера", self.action)

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def run_calibration(self):
        """Инициализирует контроллер и передает ему управление."""
        if self.calibration_controller is None:
            self.calibration_controller = CalibrationController(self.iface)

        self.calibration_controller.show_dialog()
