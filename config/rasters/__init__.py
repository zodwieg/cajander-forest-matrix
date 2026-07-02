import numpy as np
from .registry import RasterId, REGISTRY


def get_raster(raster_id: str) -> np.ndarray:
    """Точечный гейтвей для ленивого получения массива из синглтона."""
    from .rasters import RasterService

    return RasterService._instance.get_array(raster_id)
