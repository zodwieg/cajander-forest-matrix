import numpy as np
from ...config.rasters import get_raster
from ...config.coefficients import get_coefficients


def classify_biome_411(final_matrix: np.ndarray) -> np.ndarray:
    """Шаг сита №2: Выделение чахлых болотных сосняков на сфагнуме / Räme (Код 411)."""

    # 1. Стартовая маска — только неклассифицированные пиксели (свободные от кода 400)
    biome_411_mask = final_matrix == 0

    # 2. Загружаем коэффициенты для 411
    t411 = get_coefficients().biome("411")

    # 3. Динамическое сито предикатов

    # SLOPE_MAX (<) — плоский рельеф чаши болота
    if t411.is_enabled("SLOPE_MAX"):
        biome_411_mask &= get_raster("slope") < t411.SLOPE_MAX

    # TWI_MIN (>) — застойное увлажнение
    if t411.is_enabled("TWI_MIN"):
        biome_411_mask &= get_raster("TWI") > t411.TWI_MIN

    # B043_MAX (<) — снег частично перекрыт кронами и кустарничками (темнее, чем 400)
    if t411.is_enabled("B043_MAX"):
        biome_411_mask &= get_raster("B04_3") < t411.B043_MAX

    # NDRE_MIN (>) — биомассы больше, чем на открытом сфагheavy болоте (срезаем 400)
    if t411.is_enabled("NDRE_MIN"):
        biome_411_mask &= get_raster("NDRE_7") > t411.NDRE_MIN

    # NDRE_MAX (<) — биомассы меньше, чем в нормальном здоровом лесу (срезаем суходолы и тайгу)
    if t411.is_enabled("NDRE_MAX"):
        biome_411_mask &= get_raster("NDRE_7") < t411.NDRE_MAX

    # NDII_MIN (>) — высокая обводненность подложки летом
    if t411.is_enabled("NDII_MIN"):
        biome_411_mask &= get_raster("NDII_7") > t411.NDII_MIN

    # 4. Выжигаем код биома 411
    final_matrix[biome_411_mask] = 411

    return final_matrix
