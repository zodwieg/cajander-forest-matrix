from dataclasses import dataclass, field
from qgis_cajander_matrix.config import constants as c
from qgis_cajander_matrix.config.coefficients import REGISTRY, save_coefficients


@dataclass
class CajanderJobDto:
    """Чистый объект данных параметров классификации Каяндера."""

    input_file_path: str = ""
    output_path: str = ""
    raster_paths: dict[str, str] = field(default_factory=dict)


# data_binder.py
from qgis_cajander_matrix.config import constants as c
from qgis_cajander_matrix.config.coefficients import REGISTRY, save_coefficients


class QgisDataBinder:
    """Сервис, который извлекает данные из GUI QGIS и превращает их в DTO."""

    def __init__(self, algo):
        self.algo = algo

    def create_dto_from_parameters(self, parameters, context, reader) -> CajanderJobDto:
        """Собирает DTO и сбрасывает настройки из UI в глобальный синглтон."""

        # 1. Собираем то, что пользователь накрутил в интерфейсе QGIS
        ui_data = {}
        for biome_id, biome_info in REGISTRY.items():
            ui_data[biome_id] = {}
            for group_info in biome_info["groups"].values():
                for param in group_info["parameters"]:
                    param_id = param["id"]
                    qgis_param_key = f"{biome_id}_{param_id}"

                    val = self.algo.parameterAsDouble(
                        parameters, qgis_param_key, context
                    )
                    ui_data[biome_id][param_id] = val

        # 2. Сохраняем на диск. Это автоматически инвалидирует кэш в get_coefficients()!
        save_coefficients(ui_data)

        # 3. Собираем чистый DTO (без коэффициентов)
        dto = CajanderJobDto()
        dto.raster_paths = reader.get_layer_paths()
        dto.input_file_path = dto.raster_paths.get(c.PARAM_NDVI_7, "")
        dto.output_path = self.algo.parameterAsOutputLayer(
            parameters, c.PARAM_OUTPUT_RASTER, context
        )

        return dto
