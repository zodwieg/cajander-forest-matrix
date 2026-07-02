"""Модели данных для рантайм-хранилища растров."""

from dataclasses import dataclass
from qgis.core import QgsRasterLayer
from .registry import RasterId


@dataclass
class ActiveRaster:
    """Контейнер для валидированного слоя QGIS."""

    id: RasterId
    layer: QgsRasterLayer
    qgis_name: str
