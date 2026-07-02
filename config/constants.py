import os

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
