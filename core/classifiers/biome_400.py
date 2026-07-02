import numpy as np
from ...config.rasters import get_raster
from ...config.coefficients import get_coefficients


def classify_biome_400(final_matrix: np.ndarray) -> np.ndarray:
    """Шаг сита №1: Выделение открытых сфагновых болот (Код 400)."""

    # 1. Стартовая маска — только неклассифицированные пиксели
    biome_400_mask = final_matrix == 0

    # 2. Загружаем коэффициенты
    t400 = get_coefficients().biome("400")

    # 3. Динамически добавляем условия, только если они включены.
    # Если параметр выключен, растр даже не запрашивается (get_raster не вызывается).

    # SLOPE_MAX (<)
    if t400.is_enabled("SLOPE_MAX"):
        biome_400_mask &= get_raster("slope") < t400.SLOPE_MAX

    # B043_MIN (>)
    if t400.is_enabled("B043_MIN"):
        biome_400_mask &= get_raster("B04_3") > t400.B043_MIN

    # NDWI5_MIN (>)
    if t400.is_enabled("NDWI5_MIN"):
        biome_400_mask &= get_raster("NDWI_5") > t400.NDWI5_MIN

    # NDRE_MAX (<)
    if t400.is_enabled("NDRE_MAX"):
        biome_400_mask &= get_raster("NDRE_7") < t400.NDRE_MAX

    # TWI_MIN (>)
    if t400.is_enabled("TWI_MIN"):
        biome_400_mask &= get_raster("TWI") > t400.TWI_MIN

    # NDII_MIN (>)
    if t400.is_enabled("NDII_MIN"):
        biome_400_mask &= get_raster("NDII_7") > t400.NDII_MIN

    # 4. Выжигаем код биома в финальную матрицу
    final_matrix[biome_400_mask] = 400

    return final_matrix
