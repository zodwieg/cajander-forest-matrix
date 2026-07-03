"""Сервисный модуль для предобработки растров и расчета индексов."""

import os
from typing import Dict, List
from qgis.core import QgsProject, QgsRasterLayer, QgsProcessingException
from ..rasters.registry import RasterId
from .recipes import RAW_INPUTS_REGISTRY, RawInputId, PRODUCTS_RECIPES


class DataPreparationService:
    """Отвечает за физическую обработку растров: ресемплинг, репроецирование и расчет."""

    def __init__(self, reference_raster_path: str, output_dir: str):
        self.ref_path = reference_raster_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process(
        self,
        selected_products: List[RasterId],
        user_inputs: Dict[RawInputId, str],
        feedback,
    ) -> List[str]:
        """Главный рабочий цикл предобработки. Вызывается внутри QgsTask.

        user_inputs: словарь вида {"raw_b04_may": "/path/to/file.tif" или "Имя_Слоя_QGIS"}
        """
        feedback.pushInfo("🚀 Начало предобработки данных...")
        created_layers = []

        # 1. Сначала подготавливаем (нормализуем/репроецируем) все нужные сырые каналы
        # Нам нужно привести их к единой CRS и разрешению эталонного растра self.ref_path
        prepared_raw_paths: Dict[RawInputId, str] = {}

        from .model import PreprocessingDependencyResolver

        needed_raw_ids = PreprocessingDependencyResolver.resolve_required_inputs(
            selected_products
        )

        for raw_id in needed_raw_ids:
            source = user_inputs.get(raw_id)
            meta = RAW_INPUTS_REGISTRY[raw_id]
            feedback.pushInfo(f"📦 Подготовка базового канала: {meta['label']}...")

            # Здесь будет вызов gdal:warpreproject для приведения source к сетке self.ref_path
            # Для демонстрации структуры:
            output_raw_path = os.path.join(self.output_dir, f"prep_{raw_id}.tif")

            # [ТУТ БУДЕТ ГИС-КОД] -> processing.run("gdal:warp", ...)

            prepared_raw_paths[raw_id] = output_raw_path

        # 2. Теперь считаем выбранные продукты (индексы) на основе подготовленных каналов
        for prod_id in selected_products:
            recipe = PRODUCTS_RECIPES[prod_id]
            feedback.pushInfo(f"🧮 Расчет индекса/продукта: {recipe['label']}...")

            # Определяем, куда сохранить итоговый файл
            # Имя берем из твоего старого REGISTRY, чтобы алгоритм биомов потом его нашел!
            from ..rasters.registry import REGISTRY

            qgis_layer_name = REGISTRY[prod_id]["qgis_layer_name"]
            output_product_path = os.path.join(
                self.output_dir, f"{qgis_layer_name}.tif"
            )

            # В зависимости от prod_id вызываем нужную математику:
            if prod_id in ["NDVI_5", "NDVI_7"]:
                # Нужны каналы NIR и RED из рецепта
                inputs = recipe[
                    "required_inputs"
                ]  # например ["raw_b08_may", "raw_b04_may"]
                nir_path = prepared_raw_paths[inputs[0]]
                red_path = prepared_raw_paths[inputs[1]]
                # [ТУТ БУДЕТ ГИС-КОД] -> Расчет (NIR - RED) / (NIR + RED) через QgsRasterCalculator

            elif prod_id == "slope":
                dem_path = prepared_raw_paths["raw_dem"]
                # [ТУТ БУДЕТ ГИС-КОД] -> processing.run("gdal:slope", ...)

            elif prod_id == "TWI":
                dem_path = prepared_raw_paths["raw_dem"]
                # [ТУТ БУДЕТ ГИС-КОД] -> Расчет TWI через SAGA или цепочку инструментов QGIS

            # И так далее для всех индексов...

            created_layers.append(output_product_path)

        return created_layers
