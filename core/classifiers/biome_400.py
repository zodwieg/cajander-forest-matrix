import numpy as np
from ...config.rasters import get_raster
from ...config.coefficients import get_coefficients


def classify_biome_400(final_matrix: np.ndarray) -> np.ndarray:
    """Шаг сита №1: Выделение открытых сфагновых болот (Код 400)."""

    # 1. Выделяем маску еще не классифицированных пикселей
    unclassified = final_matrix == 0

    # 2. Лениво извлекаем из синглтона ТОЛЬКО те растры, которые нужны здесь.
    # Если на Шаге 1 до этого биома никто не вызывал 'slope', сервис сейчас прочитает его.
    slope = get_raster("slope")
    b04_3 = get_raster("B04_3")
    ndwi_5 = get_raster("NDWI_5")
    ndre_7 = get_raster("NDRE_7")
    twi = get_raster("TWI")
    ndii_7 = get_raster("NDII_7")

    # 3. Загружаем коэффициенты
    t400 = get_coefficients().biome("400")

    # 4. Строим строгую маску биома 400
    biome_400_mask = (
        unclassified
        & (slope < t400.SLOPE_MAX)
        & (b04_3 > t400.B043_MIN)
        & (ndwi_5 > t400.NDWI5_MIN)
        & (ndre_7 < t400.NDRE_MAX)
        & (twi > t400.TWI_MIN)
        & (ndii_7 > t400.NDII_MIN)
    )

    # 5. Выжигаем код биома в финальную матрицу
    final_matrix[biome_400_mask] = 400

    return final_matrix
