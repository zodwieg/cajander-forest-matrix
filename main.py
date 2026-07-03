# main.py
import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication, QgsProcessingProvider

from .cajander_processing_tool import CajanderMatrixAlgorithm
from .config import constants as c

# ИМПОРТ: Теперь импортируем только один главный UI-оркестратор
from .controllers.main_ui_controller import MainUIController


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

        # Единственная точка входа для всего UI (Ленивая загрузка)
        self.main_ui_controller = None
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

        # Клик вызывает метод запуска главного UI-оркестратора
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
        """Инициализирует главный контроллер интерфейса и передает ему управление."""
        if self.main_ui_controller is None:
            self.main_ui_controller = MainUIController(self.iface)

        # Он сам создаст диалог, вложенные вкладки и дочерние контроллеры
        self.main_ui_controller.show_dialog()
