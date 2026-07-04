# services/orchestrator.py

# ИСПРАВЛЕНИЕ: Импортируем строго через точку входа пакета, как это делает get_raster
from qgis_cajander_matrix.config.rasters.rasters import RasterService
from ..core import write_geotiff, generate_forest_matrix
from ..services.logger_service import CajanderLogger


class CajanderProcessingOrchestrator:

    def run(self, output_path: str) -> None:
        raster_service = RasterService()

        CajanderLogger.progress(0)
        CajanderLogger.info("Шаг 1/3: Валидация структуры проекта...")

        projection, geotransform, base_shape = raster_service.load_and_validate()

        if CajanderLogger.is_canceled():
            return
        CajanderLogger.progress(15)

        CajanderLogger.info("Шаг 2/3: Классификация 3D-матрицы лесов...")
        result_matrix = generate_forest_matrix(base_shape)

        CajanderLogger.info("Освобождение ресурсов фонового потока...")
        raster_service._cache.clear()  # Стираем объекты QgsRasterLayer
        raster_service._array_cache.clear()  # Стираем массивы NumPy

        CajanderLogger.info("Шаг 3/3: Экспорт результатов в GeoTIFF...")
        write_geotiff(output_path, result_matrix, projection, geotransform)

        raster_service.clear()
        CajanderLogger.info("Успешно завершено!")
