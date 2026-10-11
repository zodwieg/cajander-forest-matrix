import os
from typing import Dict, List
from qgis.core import QgsProcessingException

from ...config.rasters.registry import RasterId, REGISTRY
from ...config.preprocessing.recipes import (
    RAW_INPUTS_REGISTRY,
    RawInputId,
    PRODUCTS_RECIPES,
)
from ...config.preprocessing.model import PreprocessingDependencyResolver

from .raster_aligner import RasterAligner
from .index_calculators import ProductCalculatorFactory


class DataPreparationService:
    """Оркестратор подготовки данных с автоматической чисткой промежуточных слоев."""

    def __init__(self, reference_raster_path: str, output_dir: str):
        self.ref_path = reference_raster_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.aligner = RasterAligner(self.ref_path, self.output_dir)

    def process(
        self,
        selected_products: List[RasterId],
        user_inputs: Dict[RawInputId, str],
        feedback,
    ) -> List[str]:
        """Главный рабочий цикл предобработки."""
        feedback.pushInfo("🚀 Начало предобработки данных...")
        created_layers = []
        prepared_raw_paths: Dict[RawInputId, str] = {}

        needed_raw_ids = PreprocessingDependencyResolver.resolve_required_inputs(
            selected_products
        )

        try:
            # 1. Шаг выравнивания (Warp/Resample)
            for raw_id in needed_raw_ids:
                source = user_inputs.get(raw_id)
                if not source:
                    raise QgsProcessingException(
                        f"Пропущен обязательный входной слой для ID: {raw_id}"
                    )

                meta = RAW_INPUTS_REGISTRY[raw_id]
                feedback.pushInfo(f"📦 Выравнивание сетки для: {meta['label']}...")

                aligned_path = self.aligner.align(source, raw_id, feedback)
                prepared_raw_paths[raw_id] = aligned_path

            # 2. Шаг вычислений
            for prod_id in selected_products:
                recipe = PRODUCTS_RECIPES[prod_id]
                feedback.pushInfo(f"🧮 Расчет продукта: {recipe['label']}...")

                qgis_layer_name = REGISTRY[prod_id]["qgis_layer_name"]
                output_product_path = os.path.join(
                    self.output_dir, f"{qgis_layer_name}.tif"
                )

                calculator = ProductCalculatorFactory.get_calculator(prod_id)
                calculator.calculate(
                    prepared_paths=prepared_raw_paths,
                    required_inputs=recipe["required_inputs"],
                    output_path=output_product_path,
                    feedback=feedback,
                )

                created_layers.append(output_product_path)

            feedback.pushInfo("✅ Предобработка успешно завершена!")
            return created_layers

        finally:
            # 3. Гарантированная очистка временных файлов aligned_*.tif
            feedback.pushInfo("🧹 Очистка временных файлов предобработки...")
            for temp_path in prepared_raw_paths.values():
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        feedback.pushInfo(
                            f"⚠️ Не удалось удалить временный файл {temp_path}: {str(e)}"
                        )
