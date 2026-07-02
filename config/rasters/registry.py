"""Модуль данных: реестр метаданных растров и маппинг имен для поиска в QGIS."""

from typing import Literal, TypedDict

# 1. Строгие литералы для IDE. При добавлении нового растра — дописываем сюда.
RasterId = Literal[
    "DEM",
    "slope",
    "TWI",
    "B04_3",
    "NDWI_7",
    "NDVI_7",
    "NDWI_5",
    "NDVI_5",
    "NDRE_7",
    "NDII_7",
]


# 2. Описание структуры метаданных растра
class RasterMeta(TypedDict):
    id: RasterId
    qgis_layer_name: str  # Точное имя слоя в панели слоев QGIS для автопоиска
    label: str  # Человекочитаемое описание (для логов или UI)


# 3. Чистый реестр. Если опечатаетесь в ID — IDE сразу подсветит ошибку.
REGISTRY: dict[RasterId, RasterMeta] = {
    "DEM": {
        "id": "DEM",
        "qgis_layer_name": "DEM",  # Как слой назван в QGIS
        "label": "Цифровая модель рельефа",
    },
    "slope": {"id": "slope", "qgis_layer_name": "slope", "label": "Уклоны"},
    "TWI": {
        "id": "TWI",
        "qgis_layer_name": "TWI",
        "label": "Топографический индекс влажности",
    },
    "B04_3": {
        "id": "B04_3",
        "qgis_layer_name": "B04_3",
        "label": "Канал B04 (Март)",
    },
    "NDWI_7": {
        "id": "NDWI_7",
        "qgis_layer_name": "NDWI_7",
        "label": "Индекс NDWI (Июль)",
    },
    "NDVI_7": {
        "id": "NDVI_7",
        "qgis_layer_name": "NDVI_7",
        "label": "Индекс NDVI (Июль)",
    },
    "NDWI_5": {
        "id": "NDWI_5",
        "qgis_layer_name": "NDWI_5",
        "label": "Индекс NDWI (Май)",
    },
    "NDVI_5": {
        "id": "NDVI_5",
        "qgis_layer_name": "NDVI_5",
        "label": "Индекс NDVI (Май)",
    },
    "NDRE_7": {
        "id": "NDRE_7",
        "qgis_layer_name": "NDRE_7",
        "label": "Индекс NDRE (Июль)",
    },
    "NDII_7": {
        "id": "NDII_7",
        "qgis_layer_name": "NDII_7",
        "label": "Индекс NDII (Июль)",
    },
}
