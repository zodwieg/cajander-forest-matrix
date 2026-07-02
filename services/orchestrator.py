# config/orchestrator.py
import os
import numpy as np
from qgis_cajander_matrix.config import constants as c
from qgis_cajander_matrix.core import (
    read_raster_band,
    write_geotiff,
    generate_forest_matrix,
)
from qgis_cajander_matrix.ui.data_binder import CajanderJobDto


class CajanderProcessingOrchestrator:
    """Оркестратор, управляющий шагами выполнения алгоритма с жесткой валидацией."""

    def run(self, dto: CajanderJobDto, logger) -> None:
        # Полный список растров, БЕЗ которых расчет 3D-матрицы математически невозможен
        required_raster_keys = [
            c.PARAM_DEM,
            c.PARAM_SLOPE,
            c.PARAM_TWI,
            c.PARAM_B04_3,  # Март (Снег)
            c.PARAM_NDWI_7,
            c.PARAM_NDVI_7,
            c.PARAM_NDWI_5,  # Май (Вода)
            c.PARAM_NDVI_5,  # Май (Старт вегетации)
            c.PARAM_NDRE_7,  # Июль (RedEdge для пород)
            c.PARAM_NDII_7,
        ]

        logger.pushInfo("Шаг 1/3: Проверка и чтение входных растров...")

        # Валидация: проверяем наличие ключей в DTO и физическое существование файлов на диске
        for key in required_raster_keys:
            path = dto.raster_paths.get(key)
            if not path:
                raise ValueError(
                    f"Критическая ошибка: В проекте QGIS не найден слой для константы '{key}'!"
                )
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Критическая ошибка: Файл растра '{key}' отсутствует по пути: {path}"
                )

        # Читаем эталонный растр для геопривязки (NDVI_7 гарантированно на месте)
        base_path = dto.raster_paths[c.PARAM_NDVI_7]
        _, projection, geotransform = read_raster_band(base_path)

        # Читаем все растры в словарь NumPy-массивов
        # Явно подсказываем IDE тип словаря для чистоты кода
        loaded_rasters: dict[str, np.ndarray] = {}
        for key in required_raster_keys:
            logger.pushInfo(f"Чтение слоя: {key}...")
            array, _, _ = read_raster_band(dto.raster_paths[key])
            loaded_rasters[key] = array

        # Шаг 2: Обработать матрицу
        logger.pushInfo("Шаг 2/3: Классификация 3D-матрицы лесов по Каяндеру...")

        # Чистый вызов алгоритма расчёта. Оркестратор БОЛЬШЕ НЕ знает про коэффициенты!
        result_matrix = generate_forest_matrix(loaded_rasters)

        # Шаг 3: Сохранить результат
        logger.pushInfo("Шаг 3/3: Экспорт результатов в GeoTIFF...")
        write_geotiff(dto.output_path, result_matrix, projection, geotransform)
        logger.pushInfo("Успешно завершено!")
