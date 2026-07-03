# config/rasters/__init__.py
import numpy as np
from .registry import RasterId, REGISTRY


def get_raster(raster_id: str) -> np.ndarray:
    """Точечный гейтвей для ленивого получения массива из синглтона."""
    from qgis_cajander_matrix.config.rasters.rasters import RasterService

    return RasterService().get_array(raster_id)
