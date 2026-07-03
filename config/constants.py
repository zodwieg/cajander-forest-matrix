import os
from typing import Dict

from .preprocessing.recipes import GroupLiteral

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_QML_PATH = os.path.join(PROJECT_ROOT, "cajander_style.qml")

# ID параметров растров для QGIS (Остаются без изменений)
PARAM_DEM = "DEM"
PARAM_SLOPE = "slope"
PARAM_TWI = "TWI"
PARAM_B04_3 = "B04_3"
PARAM_NDWI_7 = "NDWI_7"
PARAM_NDVI_7 = "NDVI_7"
PARAM_NDWI_5 = "NDWI_5"
PARAM_NDVI_5 = "NDVI_5"
PARAM_NDRE_7 = "NDRE_7"
PARAM_NDII_7 = "NDII_7"

PARAM_OUTPUT_RASTER = "OUTPUT_RASTER"
PARAM_OUTPUT_RASTER_NAME = "forest_matrix"

# Метаданные алгоритма
PROVIDER_NAME = "cajander_provider"
ALGO_NAME = "cajander_forest_matrix"
ALGO_DISPLAY_NAME = "Генерация матрицы типов лесов (Каяндер)"
ALGO_GROUP = "Лесное хозяйство"
ALGO_GROUP_ID = "forestry"

NODATA_VALUE = -9999

# Список слоев, необходимых для работы алгоритма биомов.
# Используется для генерации UI и валидации входных данных.
REQUIRED_INPUTS = (
    ("dem", "Цифровая модель рельефа (DEM)"),
    ("slope", "Уклон (Slope)"),
    ("twi", "Индекс топографической влажности (TWI)"),
    ("b04_march", "Канал B04 (Март)"),
    ("ndwi_may", "NDWI (Май)"),
    ("ndwi_july", "NDWI (Июль)"),
    ("ndvi_may", "NDVI (Май)"),
    ("ndvi_july", "NDVI (Июль)"),
    ("ndre_july", "NDRE (Июль)"),
    ("ndii_july", "NDII (Июль)"),
)

GROUP_COLORS: Dict[GroupLiteral, str] = {
    "vegetation": "rgba(46, 139, 87, 0.08)",  # Мягкий травянисто-зеленый
    "moisture": "rgba(30, 144, 255, 0.08)",  # Мягкий небесно-синий
    "terrain": "rgba(139, 69, 19, 0.07)",  # Мягкий глиняно-коричневый
    "base_channels": "rgba(112, 128, 144, 0.08)",  # Мягкий стальной/серый для сырых данных
}
