"""Модуль описания входных (сырых) данных и рецептов для расчета индексов.

Используется исключительно формой подготовки данных и логикой предобработки.
"""

from typing import Dict, List, Literal, TypedDict
from ..rasters.registry import RasterId

# 1. Строгие литералы для сырых спутниковых данных и DEM
RawInputId = Literal[
    "raw_b04_mar",
    "raw_b04_may",
    "raw_b04_jul",
    "raw_b05_jul",
    "raw_b08_may",
    "raw_b08_jul",
    "raw_b11_may",
    "raw_b11_jul",
    "raw_dem",
]

# 2. Категории для красивой группировки чекбоксов в PyQt форме
GroupLiteral = Literal["vegetation", "moisture", "terrain", "base_channels"]


# 3. Структура метаданных для полей выбора сырых файлов
class RawInputMeta(TypedDict):
    id: RawInputId
    label: str  # Человекочитаемое имя для строки таблицы (например: "B04 (Red) | Май")
    native_res: int  # Подсказка пользователю о разрешении (10, 20, 30 м)
    suggested_name: str  # Дефолтное имя слоя в QGIS для автопоиска


# 4. Структура рецепта для расчета каждого итогового индекса
class ProductRecipeMeta(TypedDict):
    id: RasterId  # Связь со строгими ID из твоего registry.py
    label: str  # Описание для чекбокса в форме
    group: GroupLiteral  # В какую вкладку/группу UI положить этот индекс
    required_inputs: List[RawInputId]  # Список сырых каналов, нужных для расчета


# Реестр всех сырых растров, которые форма может запросить у пользователя
RAW_INPUTS_REGISTRY: Dict[RawInputId, RawInputMeta] = {
    "raw_b04_mar": {
        "id": "raw_b04_mar",
        "label": "B04 (Red) | Март",
        "native_res": 10,
        "suggested_name": "B04_March",
    },
    "raw_b04_may": {
        "id": "raw_b04_may",
        "label": "B04 (Red) | Май",
        "native_res": 10,
        "suggested_name": "B04_May",
    },
    "raw_b04_jul": {
        "id": "raw_b04_jul",
        "label": "B04 (Red) | Июль",
        "native_res": 10,
        "suggested_name": "B04_July",
    },
    "raw_b05_jul": {
        "id": "raw_b05_jul",
        "label": "B05 (RedEdge) | Июль",
        "native_res": 20,
        "suggested_name": "B05_July",
    },
    "raw_b08_may": {
        "id": "raw_b08_may",
        "label": "B08 (NIR) | Май",
        "native_res": 10,
        "suggested_name": "B08_May",
    },
    "raw_b08_jul": {
        "id": "raw_b08_jul",
        "label": "B08 (NIR) | Июль",
        "native_res": 10,
        "suggested_name": "B08_July",
    },
    "raw_b11_may": {
        "id": "raw_b11_may",
        "label": "B11 (SWIR) | Май",
        "native_res": 20,
        "suggested_name": "B11_May",
    },
    "raw_b11_jul": {
        "id": "raw_b11_jul",
        "label": "B11 (SWIR) | Июль",
        "native_res": 20,
        "suggested_name": "B11_July",
    },
    "raw_dem": {
        "id": "raw_dem",
        "label": "Copernicus DEM",
        "native_res": 30,
        "suggested_name": "Copernicus_DEM",
    },
}

# Реестр рецептов. Связывает твои RasterId с необходимыми RawInputId
PRODUCTS_RECIPES: Dict[RasterId, ProductRecipeMeta] = {
    # 🌱 ВЕГЕТАЦИОННЫЕ ИНДЕКСЫ
    "NDVI_5": {
        "id": "NDVI_5",
        "label": "NDVI Май (Растительность весной)",
        "group": "vegetation",
        "required_inputs": ["raw_b08_may", "raw_b04_may"],
    },
    "NDVI_7": {
        "id": "NDVI_7",
        "label": "NDVI Июль (Пик биомассы)",
        "group": "vegetation",
        "required_inputs": ["raw_b08_jul", "raw_b04_jul"],
    },
    "NDRE_7": {
        "id": "NDRE_7",
        "label": "NDRE Июль (Хлорофилл, RedEdge)",
        "group": "vegetation",
        "required_inputs": ["raw_b08_jul", "raw_b05_jul"],
    },
    # 💧 ИНДЕКСЫ ВЛАЖНОСТИ
    "NDWI_5": {
        "id": "NDWI_5",
        "label": "NDWI Май (Влажность растительности)",
        "group": "moisture",
        "required_inputs": ["raw_b08_may", "raw_b11_may"],
    },
    "NDWI_7": {
        "id": "NDWI_7",
        "label": "NDWI Июль (Влажность / Вода)",
        "group": "moisture",
        "required_inputs": ["raw_b08_jul", "raw_b11_jul"],
    },
    "NDII_7": {
        "id": "NDII_7",
        "label": "NDII Июль (Интенсивность увлажнения)",
        "group": "moisture",
        "required_inputs": ["raw_b08_jul", "raw_b11_jul"],
    },
    # ⛰️ МОРФОМЕТРИЯ РЕЛЬЕФА
    "DEM": {
        "id": "DEM",
        "label": "Цифровая модель рельефа (DEM)",
        "group": "terrain",
        "required_inputs": ["raw_dem"],
    },
    "slope": {
        "id": "slope",
        "label": "Уклоны (Slope)",
        "group": "terrain",
        "required_inputs": ["raw_dem"],
    },
    "TWI": {
        "id": "TWI",
        "label": "Топографический индекс влажности (TWI)",
        "group": "terrain",
        "required_inputs": ["raw_dem"],
    },
    # ❄️ БАЗОВЫЕ КАНАЛЫ
    "B04_3": {
        "id": "B04_3",
        "label": "Канал B04 Март (Снег / Ранняя весна)",
        "group": "base_channels",
        "required_inputs": ["raw_b04_mar"],
    },
}

# Человеческие названия групп для заголовков в PyQt форме
GROUP_LABELS: Dict[GroupLiteral, str] = {
    "vegetation": "Вегетационные индексы",
    "moisture": "Индексы влажности",
    "terrain": "Морфометрия рельефа",
    "base_channels": "Базовые каналы (Raw)",
}
