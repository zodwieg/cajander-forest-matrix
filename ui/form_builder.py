import os
from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
)

# Импортируем из фасада папки пакета
from ..config.coefficients import REGISTRY, get_coefficients
from ..config import constants as c


class QgisFormBuilder:
    """Сервис для динамического построения GUI интерфейса алгоритма в QGIS."""

    def __init__(self, algo):
        self.algo = algo

    def build_ui(self) -> None:
        # Загружаем текущие сохраненные коэффициенты через синглтон
        current_coeffs = get_coefficients()

        # Итерируемся по иерархическому реестру
        for biome_id, biome_info in REGISTRY.items():
            biome_name = biome_info["name"]

            for group_key, group_info in biome_info["groups"].items():
                for param in group_info["parameters"]:
                    param_id = param["id"]

                    # Формируем уникальный технический ID для QGIS формы
                    qgis_param_key = f"{biome_id}_{param_id}"

                    # Красивый читаемый лейбл для ГИС-инженера
                    display_label = f"[{biome_name}] {param['label']}"

                    # Извлекаем значение через наш строго типизированный метод .biome()
                    # VSCode здесь уже подсветит автодополнение для "400"
                    current_value = getattr(current_coeffs.biome(biome_id), param_id)

                    self.algo.addParameter(
                        QgsProcessingParameterNumber(
                            qgis_param_key,
                            display_label,
                            type=QgsProcessingParameterNumber.Type.Double,
                            defaultValue=current_value,
                            # Используем лимиты и шаг из метаданных реестра
                            minValue=param["min"],
                            maxValue=param["max"],
                        )
                    )

        # =========================================================================
        # ВЫХОДНОЙ РАСТР
        # =========================================================================
        output_param = QgsProcessingParameterRasterDestination(
            c.PARAM_OUTPUT_RASTER,
            "forest_matrix",
        )

        qml_path = c.DEFAULT_QML_PATH
        output_param.setMetadata({"PREFER_TEMPLATE": qml_path})

        self.algo.addParameter(output_param)
