import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
# PARENT_DIR — это папка, В КОТОРОЙ ЛЕЖИТ qgis_cajander_matrix (например, c:\projects)
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# Рестрим пути для Python: говорим ему смотреть на шаг выше пакета
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# 2. Безопасно импортируем ваш утилитарный модуль
try:
    from qgis_cajander_matrix.utils.dev_tools import reload_project_modules

    # Перезагружаем ВСЕ ваши модули, учитывая их новый полный путь
    # Это ваш локальный аналог HMR (Hot Module Replacement)
    reload_project_modules(
        [
            "qgis_cajander_matrix.config",
            "qgis_cajander_matrix.utils",
            "qgis_cajander_matrix.core",
            "qgis_cajander_matrix.ui",
            "qgis_cajander_matrix.services",
        ]
    )
except Exception as e:
    # Если на самом первом старте QGIS что-то пойдет не так, мы увидим ошибку в логах
    print(f"[Cajander] Ошибка горячей перезагрузки: {e}")

# 3. Стандартные импорты QGIS
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingLayerPostProcessorInterface,
    QgsProcessingParameterRasterDestination,
    QgsProject,
    QgsRasterLayer,
)
from qgis.PyQt.QtCore import QVariant

# 4. СТРОГИЕ АБСОЛЮТНЫЕ ИМПОРТЫ (Аналог using в C# с указанием полного namespace)
from .config import constants as c
from .ui import QgisFormBuilder, QgisDataBinder
from .services import CajanderProcessingOrchestrator


class CajanderMatrixAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()
        self.form_builder = QgisFormBuilder(self)
        self.ui_binder = QgisDataBinder(self)
        self.orchestrator = CajanderProcessingOrchestrator()

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                c.PARAM_OUTPUT_RASTER, c.PARAM_OUTPUT_RASTER_NAME
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # 1. Синхронизируем коэффициенты (теперь метод сам поймет, откуда их взять — из GUI QGIS или из словаря)
        self.ui_binder.sync_ui_coefficients(parameters, context)

        # 2. Получаем выходной путь напрямую из параметров QGIS
        output_path = self.parameterAsOutputLayer(
            parameters, c.PARAM_OUTPUT_RASTER, context
        )

        # 3. Запуск расчетов оркестратором (чистая бизнес-логика в фоне)
        if feedback:
            feedback.pushInfo("Старт фонового расчета матрицы...")

        self.orchestrator.run(output_path, feedback)

        # Возвращаем словарь с результатом, который Контроллер заберет в главном потоке
        return {c.PARAM_OUTPUT_RASTER: output_path}

    def name(self):
        return c.ALGO_NAME

    def displayName(self):
        return c.ALGO_DISPLAY_NAME

    def group(self):
        return c.ALGO_GROUP

    def groupId(self):
        return c.ALGO_GROUP_ID

    def createInstance(self):
        return CajanderMatrixAlgorithm()

    def createCustomParametersWidget(self, parent):
        # Возвращаем None, чтобы QGIS не пытался строить дефолтный UI внутри себя
        return None
