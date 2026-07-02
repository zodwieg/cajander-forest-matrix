from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
)
from qgis_cajander_matrix.config import coefficients as coef
from qgis_cajander_matrix.config import constants as c


class QgisFormBuilder:
    """Сервис для динамического построения GUI интерфейса алгоритма в QGIS."""

    def __init__(self, algo):
        self.algo = algo

    def build_ui(self) -> None:
        # Загружаем текущие сохраненные коэффициенты как объект
        current_coeffs = coef.load_coefficients()

        # Автоматически генерируем все числовые поля ввода
        for item in coef.REGISTRY:
            param_id = item["id"]
            # Вытаскиваем значение из объекта по текстовому имени переменной
            current_value = getattr(current_coeffs, param_id)

            self.algo.addParameter(
                QgsProcessingParameterNumber(
                    param_id,
                    item["label"],
                    type=QgsProcessingParameterNumber.Type.Double,
                    defaultValue=current_value,
                )
            )

        # =========================================================================
        # ВЫХОДНОЙ РАСТР
        # =========================================================================
        # 1. Сначала создаем объект параметра и сохраняем его в переменную
        output_param = QgsProcessingParameterRasterDestination(
            c.PARAM_OUTPUT_RASTER,
            "forest_matrix",
        )

        # 2. Настраиваем метаданные стиля для созданного объекта
        import os

        qml_path = c.DEFAULT_QML_PATH

        # Используем стандартный ключ для принудительного маппинга QML
        output_param.setMetadata({"PREFER_TEMPLATE": qml_path})

        # 3. И только теперь ОДИН РАЗ регистрируем его в алгоритме
        self.algo.addParameter(output_param)
