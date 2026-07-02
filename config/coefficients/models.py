"""Модуль строго типизированных моделей данных."""

from typing import Any, Dict
from .registry import BiomeId, ParamId


class ParameterValue:
    """Контейнер для значения параметра и его статуса."""

    def __init__(self, value: float, is_enabled: bool = True):
        self.value = value
        self.is_enabled = is_enabled

    def to_dict(self) -> dict:
        """Для удобного сохранения в JSON."""
        return {"value": self.value, "is_enabled": self.is_enabled}


class BiomeConfig:
    """Обёртка над биомом."""

    def __init__(self, biome_data: Dict[ParamId, ParameterValue]):
        self._data = biome_data

    def __getattr__(self, name: ParamId) -> float:
        """Возвращает значение float для обратной совместимости и простоты в алгоритмах."""
        if name not in self._data:
            raise AttributeError(f"Коэффициент '{name}' не настроен для этого биома.")

        param = self._data[name]
        return param.value

    def is_enabled(self, name: ParamId) -> bool:
        """Проверка, включен ли коэффициент."""
        if name not in self._data:
            return False
        return self._data[name].is_enabled

    def get_raw(self, name: ParamId) -> ParameterValue:
        """Получить полный объект параметра."""
        if name not in self._data:
            raise AttributeError(f"Коэффициент '{name}' не настроен.")
        return self._data[name]


class CalibrationCoefficients:
    """Главный контейнер коэффициентов."""

    def __init__(self, full_data: dict):
        """
        Принимает словарь структуры:
        {
            "400": {
                "SLOPE_MAX": {"value": 2.0, "is_enabled": True},
                "B043_MIN": {"value": 0.1, "is_enabled": False}
            }
        }
        """
        self._biomes: Dict[BiomeId, BiomeConfig] = {}

        for biome_id, params in full_data.items():
            biome_params = {}
            for param_id, param_body in params.items():
                # Поддержка старого формата (если в файле был просто float)
                if isinstance(param_body, (int, float)):
                    biome_params[param_id] = ParameterValue(float(param_body))
                else:
                    biome_params[param_id] = ParameterValue(
                        value=param_body.get("value", 0.0),
                        is_enabled=param_body.get("is_enabled", True),
                    )
            self._biomes[biome_id] = BiomeConfig(biome_params)

    def biome(self, biome_id: BiomeId) -> BiomeConfig:
        if biome_id not in self._biomes:
            return BiomeConfig({})
        return self._biomes[biome_id]

    def to_dict(self) -> dict:
        """Сериализация всего конфига для записи в файл."""
        return {
            biome_id: {
                param_id: param_obj.to_dict()
                for param_id, param_obj in biome_config._data.items()
            }
            for biome_id, biome_config in self._biomes.items()
        }
