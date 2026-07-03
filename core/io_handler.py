"""Низкоуровневый слой: Чистая логика работы с GDAL для чтения и записи GeoTIFF."""

import numpy as np
from osgeo import gdal
from ..config.constants import NODATA_VALUE


def read_raster_band(
    raster_path: str, band_num: int = 1
) -> tuple[np.ndarray, str, tuple]:
    """Читает растровый банд и возвращает массив NumPy, проекцию и геотрансформ."""
    dataset = gdal.Open(raster_path)
    if not dataset:
        raise FileNotFoundError(f"Не удалось открыть растр по пути: {raster_path}")

    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    band = dataset.GetRasterBand(band_num)
    array = band.ReadAsArray()

    # ИСПРАВЛЕНИЕ: Сначала уничтожаем ссылку на банд, затем на сам датасет
    band = None
    dataset = None

    return array, projection, geotransform


def write_geotiff(
    output_path: str,
    data_array: np.ndarray,
    projection: str,
    geotransform: tuple,
    dtype=gdal.GDT_Int16,
) -> None:
    """Создает файл GeoTIFF из массива NumPy, используя пространственную привязку."""
    driver = gdal.GetDriverByName("GTiff")
    height, width = data_array.shape

    out_dataset = driver.Create(output_path, width, height, 1, dtype)
    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(projection)

    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data_array)
    out_band.SetNoDataValue(NODATA_VALUE)

    # ИСПРАВЛЕНИЕ: Сбрасываем кэш всего датасета, а не только отдельного банда
    out_band.FlushCache()
    out_dataset.FlushCache()

    # КРИТИЧЕСКИ ВАЖНО ДЛЯ WINDOWS:
    # Сначала обнуляем дочерний банд, затем закрываем родительский датасет
    out_band = None
    out_dataset = None
