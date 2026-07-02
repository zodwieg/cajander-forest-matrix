from ..config.rasters.rasters import RasterService
from ..core import write_geotiff, generate_forest_matrix


class CajanderProcessingOrchestrator:

    def run(self, output_path: str, logger) -> None:
        raster_service = RasterService()
        logger.pushInfo("Шаг 1/3: Валидация структуры проекта...")
        # Быстрая валидация без чтения тяжелых данных в RAM
        projection, geotransform, base_shape = raster_service.load_and_validate(logger)

        logger.pushInfo("Шаг 2/3: Классификация 3D-матрицы лесов по Каяндеру...")
        # Передаем только размеры. Внутри сита растры загрузятся лениво.
        result_matrix = generate_forest_matrix(base_shape)

        logger.pushInfo("Шаг 3/3: Экспорт результатов в GeoTIFF...")
        write_geotiff(output_path, result_matrix, projection, geotransform)

        # Освобождаем гигабайты памяти NumPy-массивов
        raster_service.clear()
        logger.pushInfo("Успешно завершено!")
