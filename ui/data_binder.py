from dataclasses import dataclass, field
from ..config import constants as c
from ..config.coefficients import REGISTRY, save_coefficients


@dataclass
class CajanderJobDto:
    """Чистый объект данных параметров классификации Каяндера."""

    input_file_path: str = ""
    output_path: str = ""
    raster_paths: dict[str, str] = field(default_factory=dict)


class QgisDataBinder:
    """Сервис, который извлекает данные и сохраняет их в конфигурацию."""

    def __init__(self, algo):
        self.algo = algo

    def sync_ui_coefficients(self, parameters, context) -> None:
        """Считывает коэффициенты и сбрасывает их в глобальный синглтон."""

        # СЦЕНАРИЙ А: Алгоритм запущен из нашего кастомного контроллера калибровки.
        # Контроллер передал уже готовый собранный стейт в ключе 'COEFFICIENTS'.
        if "COEFFICIENTS" in parameters:
            ui_data = parameters["COEFFICIENTS"]
            save_coefficients(ui_data)
            return

        # СЦЕНАРИЙ Б: Алгоритм запущен стандартно через нативное окно QGIS Processing.
        # Собираем данные поштучно из виджетов QGIS.
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

        # Сохраняем на диск / обновляем синглтон
        save_coefficients(ui_data)
