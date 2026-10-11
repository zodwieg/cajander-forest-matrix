import os
from abc import ABC, abstractmethod
from typing import List, Dict
import processing
from ...config.preprocessing.formulas import INDEX_FORMULAS


class BaseProductCalculator(ABC):
    @abstractmethod
    def calculate(
        self,
        prepared_paths: Dict[str, str],
        required_inputs: List[str],
        output_path: str,
        feedback,
    ) -> str:
        pass


class GdalFormulaCalculator(BaseProductCalculator):
    """Счет классических индексов через GDAL с учетом NoData и номеров каналов."""

    def __init__(self, prod_id: str):
        self.prod_id = prod_id

    def calculate(
        self,
        prepared_paths: Dict[str, str],
        required_inputs: List[str],
        output_path: str,
        feedback,
    ) -> str:
        formula = INDEX_FORMULAS.get(self.prod_id)
        if not formula:
            raise ValueError(f"Формула для {self.prod_id} не найдена!")

        # Базовые параметры калькулятора
        params = {
            "FORMULA": formula,
            "NoData": -9999,
            "RTYPE": 5,  # 5 = Float32 в параметрах gdal:rastercalculator
            "ROPTIONS": "COMPRESS=LZW",
            "OUTPUT": output_path,
        }

        # Списки букв для сопоставления инпутов и номеров их внутренних каналов
        input_letters = [
            "INPUT_A",
            "INPUT_B",
            "INPUT_C",
            "INPUT_D",
            "INPUT_E",
            "INPUT_F",
        ]
        band_letters = ["BAND_A", "BAND_B", "BAND_C", "BAND_D", "BAND_E", "BAND_F"]

        for idx, raw_id in enumerate(required_inputs):
            if idx < len(input_letters):
                # Привязываем путь к выровненному TIF файлу (например, 'INPUT_A')
                params[input_letters[idx]] = prepared_paths[raw_id]
                # Явно указываем первый растровый канал (например, 'BAND_A' = 1)
                params[band_letters[idx]] = 1

        processing.run("gdal:rastercalculator", params, feedback=feedback)
        return output_path


class SlopeCalculator(BaseProductCalculator):
    """Рассчитывает крутизну склонов через GDAL."""

    def calculate(
        self,
        prepared_paths: Dict[str, str],
        required_inputs: List[str],
        output_path: str,
        feedback,
    ) -> str:
        dem_path = prepared_paths["raw_dem"]
        params = {
            "INPUT": dem_path,
            "BAND": 1,
            "AS_PERCENT": False,  # В градусах
            "OPTIONS": "COMPRESS=LZW",
            "OUTPUT": output_path,
        }
        processing.run("gdal:slope", params, feedback=feedback)
        return output_path


class TwiCalculator(BaseProductCalculator):
    """Рассчитывает TWI через нативный GRASS7 инструмент r.topidx."""

    def calculate(
        self,
        prepared_paths: Dict[str, str],
        required_inputs: List[str],
        output_path: str,
        feedback,
    ) -> str:
        dem_path = prepared_paths["raw_dem"]
        base_dir = os.path.dirname(output_path)

        # Временные файлы GRASS (будут удалены оркестратором)
        accumulation_temp = os.path.join(base_dir, "temp_grass_accum.tif")

        # Шаг 1. Считаем Flow Accumulation через GRASS watershed
        feedback.pushInfo(
            "🌊 Шаг TWI 1/2: Расчет накопления потока (GRASS r.watershed)..."
        )
        watershed_params = {
            "elevation": dem_path,
            "threshold": 100,
            "accumulation": accumulation_temp,
            "GRASS_REGION_PARAMETER": dem_path,  # Привязываем регион GRASS строго к сетке нашего DEM
        }
        processing.run("grass:r.watershed", watershed_params, feedback=feedback)

        # Шаг 2. Считаем топографический индекс влажности (r.topidx)
        feedback.pushInfo("📐 Шаг TWI 2/2: Генерация индекса TWI (GRASS r.topidx)...")
        topidx_params = {
            "input": dem_path,
            "relevance": accumulation_temp,
            "output": output_path,
            "GRASS_REGION_PARAMETER": dem_path,
        }
        processing.run("grass:r.topidx", topidx_params, feedback=feedback)

        # Чистим внутренний временный файл шага 1
        if os.path.exists(accumulation_temp):
            os.remove(accumulation_temp)

        return output_path


class ProductCalculatorFactory:
    @staticmethod
    def get_calculator(prod_id: str) -> BaseProductCalculator:
        if prod_id == "slope":
            return SlopeCalculator()
        elif prod_id == "TWI":
            return TwiCalculator()
        else:
            return GdalFormulaCalculator(prod_id)
