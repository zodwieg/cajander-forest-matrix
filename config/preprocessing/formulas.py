"""Конфигурация строковых формул для растрового калькулятора GDAL/QGIS."""

from typing import Dict
from ...config.rasters.registry import RasterId

# Формулы пишутся под синтаксис gdal:rastercalculator (где слои именуются как A, B, C...)
INDEX_FORMULAS: Dict[RasterId, str] = {
    "DEM": "A",
    "NDVI_5": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=Red
    "NDVI_7": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=Red
    "NDRE_7": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=RedEdge
    "NDWI_5": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=SWIR
    "NDWI_7": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=SWIR
    "NDII_7": "(A.astype(float) - B.astype(float)) / (A + B + 1e-10)",  # A=NIR, B=SWIR
    "B04_3": "A",  # Просто копирование/проброс выровненного канала
}
