import os
import sys
from qgis_cajander_matrix.config import constants as c

# 1. Поднимаемся на один уровень выше, чтобы qgis_cajander_matrix стал видимым пакетом
PARENT_DIR = os.path.dirname(c.PROJECT_ROOT)
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
)
from qgis.PyQt.QtCore import QVariant

# 4. СТРОГИЕ АБСОЛЮТНЫЕ ИМПОРТЫ (Аналог using в C# с указанием полного namespace)

from qgis_cajander_matrix.ui import QgisFormBuilder, QgisDataBinder
from qgis_cajander_matrix.core.io_handler import QgisProjectReader
from qgis_cajander_matrix.services import CajanderProcessingOrchestrator


class CajanderRasterStyler(QgsProcessingLayerPostProcessorInterface):
    """Постпроцессор, который принудительно красит растр ПОСЛЕ его полной загрузки."""

    def postProcessLayer(self, layer, context, feedback):
        if not layer or not layer.isValid():
            return

        if feedback:
            feedback.pushInfo("Применяем стиль Каяндера к растру...")

        # ВАРИАНТ А: Через код (с обновленными лимитами min/max)

        # ---------------------------------------------------------------------
        # ВАРИАНТ Б (АЛЬТЕРНАТИВНЫЙ): Автоматическое применение готового QML-файла
        # Если Вариант А снова выдаст ч/б, просто раскомментируйте строки ниже,
        # предварительно сохранив правильный стиль из интерфейса QGIS в файл .qml
        #
        import os

        qml_path = c.DEFAULT_QML_PATH
        error_msg = ""
        success, error_msg = layer.loadNamedStyle(qml_path)
        if not success and feedback:
            feedback.pushDebugInfo(f"Ошибка загрузки QML: {error_msg}")
        # ---------------------------------------------------------------------

        # Принудительно обновляем кэш и заставляем QGIS перерисовать легенду в панели
        layer.triggerRepaint()
        from qgis.core import QgsProject

        QgsProject.instance().layerTreeRoot().findLayer(layer.id()).refresh()


class CajanderMatrixAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()
        self.form_builder = QgisFormBuilder(self)
        self.ui_binder = QgisDataBinder(self)
        self.orchestrator = CajanderProcessingOrchestrator()

    def initAlgorithm(self, config=None):
        self.form_builder.build_ui()

    def processAlgorithm(self, parameters, context, feedback):
        # 1. Готовим ридер проекта и собираем DTO
        reader = QgisProjectReader(feedback)
        dto = self.ui_binder.create_dto_from_parameters(parameters, context, reader)

        # 2. Запуск ваших расчетов
        self.orchestrator.run(dto, feedback)

        # =========================================================================
        # ХИТРЫЙ ХАК: САМИ ЗАГРУЖАЕМ И КРАСИМ СЛОЙ, МИНУЯ БАГИ СИСТЕМЫ СТИЛЕЙ
        # =========================================================================
        import os
        from qgis.core import (
            QgsRasterLayer,
            QgsProject,
        )
        from qgis.PyQt.QtGui import QColor

        if feedback:
            feedback.pushInfo("Принудительно загружаем растр и накатываем QML...")

        # Создаем полноценный слой напрямую из созданного файла
        layer_name = "forest_matrix"
        final_layer = QgsRasterLayer(dto.output_path, layer_name)

        if final_layer.isValid():
            # Накатываем ваш сохраненный QML файл с адаптивной палитрой
            qml_path = c.DEFAULT_QML_PATH
            final_layer.loadNamedStyle(qml_path)

            # Добавляем растр напрямую в текущий проект QGIS
            QgsProject.instance().addMapLayer(final_layer)

        if feedback:
            feedback.pushInfo(
                "Алгоритм успешно завершен, передаем управление интерфейсу."
            )

        # Возвращаем пустой словарь, совместимый с C++ QVariantMap
        return dict()

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
