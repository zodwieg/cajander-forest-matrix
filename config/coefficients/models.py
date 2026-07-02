"""Модуль строго типизированных моделей данных."""

from typing import Any
from .registry import BiomeId, ParamId


class BiomeConfig:
    """Обёртка над биомом.

    Для разработчика это объект с автодополнением, внутри — эффективный поиск по словарю.
    """

    def __init__(self, biome_data: dict[str, float]):
        self._data = biome_data

    # Хитрый трюк: заставляем IDE думать, что при обращении к свойству
    # мы передаем ParamId и получаем float.
    def __getattr__(self, name: ParamId) -> float:
        # Защита от опечаток в рантайме
        if name not in self._data:
            raise AttributeError(f"Коэффициент '{name}' не настроен для этого биома.")
        return self._data[name]


class CalibrationCoefficients:
    """Главный контейнер коэффициентов."""

    def __init__(self, full_data: dict[str, dict[str, float]]):
        self._biomes = {
            biome_id: BiomeConfig(biome_data)
            for biome_id, biome_data in full_data.items()
        }

    # Подсказываем IDE, что метод принимает строго валидный BiomeId
    def biome(self, biome_id: BiomeId) -> BiomeConfig:
        if biome_id not in self._biomes:
            return BiomeConfig({})
        return self._biomes[biome_id]
