"""Модуль чистой бизнес-логики (Модели) для анализа зависимостей растров."""

from typing import List, Set
from ..rasters.registry import RasterId
from .recipes import PRODUCTS_RECIPES, RawInputId


class PreprocessingDependencyResolver:
    """Утилита для расчета зависимостей между индексами и сырыми растрами.

    Не хранит состояние UI, используется контроллером для вычисления логики.
    """

    @staticmethod
    def resolve_required_inputs(selected_products: List[RasterId]) -> List[RawInputId]:
        """Принимает список выбранных ID индексов и возвращает уникальный,
        отсортированный список ID сырых растров, необходимых для их расчета.
        """
        required_set: Set[RawInputId] = set()

        for prod_id in selected_products:
            if prod_id in PRODUCTS_RECIPES:
                recipe = PRODUCTS_RECIPES[prod_id]["required_inputs"]
                required_set.update(recipe)

        return sorted(list(required_set))
