import json
from dataclasses import dataclass, field
from ..config import constants as c
from ..config.coefficients import save_coefficients
from ..config.coefficients.coefficients import CalibrationCoefficients


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
        """Считывает коэффициенты из параметров алгоритма и сбрасывает их в синглтон."""
        raw_data = parameters.get("COEFFICIENTS", {})

        # Защита от QGIS-специфики: десериализация строки в dict, если QGIS превратил его в строку
        if isinstance(raw_data, str):
            try:
                raw_data = json.loads(raw_data)
            except Exception:
                raw_data = {}

        # Строгий маппинг данных (Data Mapping) перед передачей в доменную модель
        normalized = {}
        for biome_id, params in raw_data.items():
            normalized[biome_id] = {}
            for pid, pbody in params.items():
                if isinstance(pbody, dict):
                    # Новый формат с флагами из диалога калибровки
                    normalized[biome_id][pid] = pbody
                else:
                    # На случай, если проскочило старое плоское число float
                    normalized[biome_id][pid] = {
                        "value": float(pbody),
                        "is_enabled": True,
                    }

        # Вызываем строгое сохранение доменного объекта
        save_coefficients(CalibrationCoefficients(normalized))
