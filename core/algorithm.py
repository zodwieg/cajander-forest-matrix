import numpy as np
from .classifiers import classify_biome_400


def generate_forest_matrix(base_shape: tuple[int, int]) -> np.ndarray:
    """Оркестратор последовательного классификатора («Сито»)."""

    # Инициализируем матрицу нулями на основе размера эталона
    final_matrix = np.zeros(base_shape, dtype=np.int16)

    # --- НАЧАЛО СИТА ---

    # Шаг 1. Открытое сфагновое болото (Функция сама заберет из сервиса нужные растры)
    classify_biome_400(final_matrix=final_matrix)

    # Шаг 2. Следующий биом (Ему могут понадобиться другие растры, и он возьмет их сам)
    # classify_biome_500(final_matrix=final_matrix)

    return final_matrix
