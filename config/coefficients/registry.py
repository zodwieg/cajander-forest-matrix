"""Модуль данных: реестр коэффициентов и метаданные для IDE."""

from typing import Literal, TypedDict, List

# 1. Объявляем строгие литералы для IDE.
# При добавлении нового биома или параметра — дописываем их сюда.
BiomeId = Literal["400", "500"]
ParamId = Literal["SLOPE_MAX", "B043_MIN", "NDWI5_MIN", "NDRE_MAX"]


# 2. Описываем структуры типов для внутренней кухни плагина (Type Hinting для UI)
class ParameterMeta(TypedDict):
    id: ParamId
    label: str
    default: float
    min: float
    max: float
    step: float


class GroupMeta(TypedDict):
    label: str
    parameters: List[ParameterMeta]


class BiomeMeta(TypedDict):
    name: str
    groups: dict[str, GroupMeta]


# 3. Чистый реестр, защищенный типами.
# Если вы опечатаетесь в ID биома или параметра — VSCode сразу подсветит это красным!
REGISTRY: dict[BiomeId, BiomeMeta] = {
    "400": {
        "name": "Neva (открытое сфагновое болото)",
        "groups": {
            "terrain": {
                "label": "Рельеф и топография",
                "parameters": [
                    {
                        "id": "SLOPE_MAX",
                        "label": "Maximum slope",
                        "default": 2.0,
                        "min": 0.0,
                        "max": 45.0,
                        "step": 0.1,
                    }
                ],
            },
            "spectral": {
                "label": "Спектральные индексы",
                "parameters": [
                    {
                        "id": "B043_MIN",
                        "label": "Minimum March B04",
                        "default": 0.8,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                    {
                        "id": "NDWI5_MIN",
                        "label": "Minimum May NDWI",
                        "default": 0.4,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                    {
                        "id": "NDRE_MAX",
                        "label": "Maximum NDRE",
                        "default": 0.3,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.01,
                    },
                ],
            },
        },
    }
}
