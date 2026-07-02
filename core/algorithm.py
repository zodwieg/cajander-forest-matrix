import numpy as np
from qgis_cajander_matrix.core.classifiers import classify_biome_400


def generate_forest_matrix(rasters: dict[str, np.ndarray]) -> np.ndarray:
    """Оркестратор последовательного классификатора («Сито»).

    Каждая функция биома забирает неразмеченные пиксели, валидирует их
    и выжигает свой трехзначный код в итоговую матрицу.
    """
    # Инициализируем итоговый растр нулями (0 - не классифицировано)
    any_raster = next(iter(rasters.values()))
    final_matrix = np.zeros(any_raster.shape, dtype=np.int16)

    # --- НАЧАЛО СИТА ---

    # Шаг 1. Открытое сфагновое болото / Топь (Avosuo / Neva)
    # Массив final_matrix изменится прямо внутри функции (in-place)
    classify_biome_400(final_matrix=final_matrix, rasters=rasters)

    # Шаг 2. (Сюда вы добавите следующий биом: 500, 600 и т.д.)
    # classify_biome_500(final_matrix=final_matrix, rasters=rasters, coeffs=coeffs)

    return final_matrix
