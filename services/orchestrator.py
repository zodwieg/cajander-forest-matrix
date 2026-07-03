# services/orchestrator.py

# ИСПРАВЛЕНИЕ: Импортируем строго через точку входа пакета, как это делает get_raster
from qgis_cajander_matrix.config.rasters.rasters import RasterService
from ..core import write_geotiff, generate_forest_matrix


class CajanderProcessingOrchestrator:

    def run(self, output_path: str, logger) -> None:
        raster_service = RasterService()
        logger.pushInfo("Шаг 1/3: Валидация структуры проекта...")
        projection, geotransform, base_shape = raster_service.load_and_validate(logger)

        logger.pushInfo("Шаг 2/3: Классификация 3D-матрицы лесов по Каяндеру...")
        result_matrix = generate_forest_matrix(base_shape)

        logger.pushInfo("Освобождение ресурсов фонового потока...")
        raster_service._cache.clear()  # Стираем объекты QgsRasterLayer
        raster_service._array_cache.clear()  # Стираем массивы NumPy

        logger.pushInfo("Шаг 3/3: Экспорт результатов в GeoTIFF...")
        write_geotiff(output_path, result_matrix, projection, geotransform)

        # РЕШЕНИЕ: Просто вызываем очистку кэша NumPy.
        # Никаких принудительных удалений самого класса из памяти здесь делать не нужно!
        raster_service.clear()
        logger.pushInfo("Успешно завершено!")
