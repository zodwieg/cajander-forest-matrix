import numpy as np
from qgis_cajander_matrix.config import constants as c
from qgis_cajander_matrix.config.coefficients import get_coefficients


def classify_biome_400(
    final_matrix: np.ndarray, rasters: dict[str, np.ndarray]
) -> np.ndarray:
    """Шаг сита №1: Выделение открытых сфагновых болот (Код 400)."""

    # 1. Выделяем маску еще не классифицированных пикселей
    unclassified = final_matrix == 0

    # 2. Извлекаем только те растры, которые нужны для этого биома
    slope = rasters[c.PARAM_SLOPE]
    b04_3 = rasters[c.PARAM_B04_3]  # Март (снег/луг)
    ndwi_5 = rasters[c.PARAM_NDWI_5]  # Май (весенняя вода)
    ndre_7 = rasters[c.PARAM_NDRE_7]  # Июль (хлорофилл/биомасса)

    t400 = get_coefficients().biome("400")

    # 4. Строим строгую маску биома 400
    # Пиксель должен подходить по всем условиям И быть свободным
    biome_400_mask = (
        unclassified
        & (slope < t400.SLOPE_MAX)  # Плоский рельеф
        & (b04_3 > t400.B043_MIN)  # Открытый мартовский снег (нет крон деревьев)
        & (ndwi_5 > t400.NDWI5_MIN)  # Весеннее сильное переувлажнение / застой воды
        & (ndre_7 < t400.NDRE_MAX)  # Низкая плотность летней древесной биомассы
    )

    # 5. Выжигаем код биома в финальную матрицу
    final_matrix[biome_400_mask] = 400

    return final_matrix
