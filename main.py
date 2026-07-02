from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication, QgsProcessingProvider

# Импортируем ваш класс алгоритма
from .cajander_processing_tool import CajanderMatrixAlgorithm
from .config import constants as c


class CajanderMatrixProvider(QgsProcessingProvider):
    """Провайдер, который регистрирует наши инструменты в панели Processing."""

    def unload(self):
        """Очистка при отключении плагина."""
        pass

    def loadAlgorithms(self):
        """Сюда добавляем все наши алгоритмы."""
        self.addAlgorithm(CajanderMatrixAlgorithm())

    def id(self):
        return c.PROVIDER_NAME

    def name(self):
        return "Матрица Каяндера"

    def icon(self):
        """Возвращает стандартную системную иконку для папки в Processing."""
        return QIcon()


class CajanderPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None  # Ссылка на будущую кнопку

    def initGui(self):
        # 1. (Ваш старый код) HMR перезагрузка и регистрация провайдера
        self.provider = CajanderMatrixProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        # 2. Создаем экшен (кнопку) для тулбара
        # Укажем стандартную иконку шестеренки, позже заменим на вашу .png
        icon = QIcon(QgsApplication.reportStyleSheet())

        self.action = QAction(
            icon, "Запустить матрицу Каяндера", self.iface.mainWindow()
        )

        # Подключаем клик на кнопку к запуску вашего алгоритма в интерфейсе QGIS
        self.action.triggered.connect(self.run_algorithm_gui)

        # Добавляем кнопку на стандартный тулбар плагинов QGIS
        self.iface.addPluginToRasterMenu(
            "Матрица Каяндера", self.action
        )  # В меню "Растр"
        self.iface.addRasterToolBarIcon(self.action)  # На панель инструментов "Растр"

    def unload(self):
        # Обязательно удаляем кнопку из интерфейса при отключении плагина!
        if self.action:
            self.iface.removeRasterToolBarIcon(self.action)
            self.iface.removePluginRasterMenu("Матрица Каяндера", self.action)

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def run_algorithm_gui(self):
        """Метод, который открывает стандартное окно вашего алгоритма при клике на кнопку."""
        import processing

        # Вызываем окно геообработки по ID провайдера и ID алгоритма
        # Формат: 'id_провайдера:id_алгоритма'
        algorithm_id = f"{c.PROVIDER_NAME}:{c.ALGO_NAME}"
        processing.execInGui(algorithm_id, {})
