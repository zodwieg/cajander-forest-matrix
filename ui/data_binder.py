from dataclasses import dataclass, field
from qgis_cajander_matrix.config import constants as c
from qgis_cajander_matrix.config import coefficients as coef


@dataclass
class CajanderJobDto:
    """Чистый объект данных параметров классификации Каяндера."""

    input_file_path: str = ""
    output_path: str = ""
    # Вместо dict[str, float] теперь храним строго наш объект коэффициентов
    coefficients: coef.CalibrationCoefficients = None
    raster_paths: dict[str, str] = field(default_factory=dict)


class QgisDataBinder:
    """Сервис, который извлекает данные из GUI QGIS и превращает их в DTO."""

    def __init__(self, algo):
        self.algo = algo
        # Больше никакой приватный список полей здесь НЕ нужен!

    def create_dto_from_parameters(self, parameters, context, reader) -> CajanderJobDto:
        """Собирает DTO на основе текущих параметров в интерфейсе QGIS."""
        dto = CajanderJobDto()

        # 1. Автоматически собираем ВСЕ коэффициенты из реестра coefficients.py
        ui_data = {}
        for item in coef.REGISTRY:
            param_id = item["id"]
            val = self.algo.parameterAsDouble(parameters, param_id, context)
            ui_data[param_id] = val

        # 2. ПРЯМО ОЧЕНЬ НАДЁЖНО сохраняем их в JSON при каждом запуске
        coef.save_coefficients(ui_data)

        # 3. Маппим данные в объект с доступом через точку и кладем в DTO
        dto.coefficients = coef.CalibrationCoefficients(ui_data)

        # 4. Собираем пути к зарегистрированным растрам
        dto.raster_paths = reader.get_layer_paths()

        # В качестве базового пути для метаданных растра берем NDVI_7
        dto.input_file_path = dto.raster_paths.get(c.PARAM_NDVI_7, "")

        # 5. Путь для сохранения результирующего растра
        dto.output_path = self.algo.parameterAsOutputLayer(
            parameters, c.PARAM_OUTPUT_RASTER, context
        )

        return dto
