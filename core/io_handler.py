# core/io_handler.py
import numpy as np
from osgeo import gdal
from qgis.core import QgsProject, QgsRasterLayer, QgsProcessingException
from qgis_cajander_matrix.config.constants import NODATA_VALUE
from qgis_cajander_matrix.config import constants as c


class QgisProjectReader:
    """ВЫСОКИЙ СЛОЙ: Автоматически находит слои в QGIS и отдает пути к файлам."""

    def __init__(self, feedback):
        self.feedback = feedback

    def get_layer_paths(self) -> dict[str, str]:
        """
        Находит растры в проекте QGIS по именам и возвращает словарь путей на диске.
        """
        required_names = {
            c.PARAM_DEM: "DEM",
            c.PARAM_SLOPE: "slope",
            c.PARAM_TWI: "TWI",
            c.PARAM_B04_3: "B04_3",
            c.PARAM_NDWI_7: "NDWI_7",
            c.PARAM_NDVI_7: "NDVI_7",
            c.PARAM_NDWI_5: "NDWI_5",
            c.PARAM_NDVI_5: "NDVI_5",
            c.PARAM_NDRE_7: "NDRE_7",
            c.PARAM_NDII_7: "NDII_7",
        }

        project = QgsProject.instance()
        file_paths = {}

        self.feedback.pushInfo("🔍 Автоматический поиск слоев в проекте...")

        for param_id, layer_name in required_names.items():
            layers = project.mapLayersByName(layer_name)

            if not layers:
                raise QgsProcessingException(
                    f"Ошибка: Не найден слой '{layer_name}'. Добавьте его в QGIS!"
                )

            layer = layers[0]
            if layer.type() != QgsRasterLayer.RasterLayer:
                raise QgsProcessingException(
                    f"Ошибка: Слой '{layer_name}' должен быть растровым!"
                )

            # Ключевой момент: забираем абсолютный путь к файлу на диске (.tif)
            file_paths[param_id] = layer.source()
            self.feedback.pushInfo(
                f"   [ОК] Слой '{layer_name}' привязан к пути: {layer.source()}"
            )

        return file_paths


# НИЗКИЙ СЛОЙ: Ваша чистая логика работы с GDAL (остается без изменений)


def read_raster_band(
    raster_path: str, band_num: int = 1
) -> tuple[np.ndarray, str, tuple]:
    """Reads a raster band and returns the array, projection, and geotransform."""
    dataset = gdal.Open(raster_path)
    if not dataset:
        raise FileNotFoundError(f"Не удалось открыть растр по пути: {raster_path}")

    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    band = dataset.GetRasterBand(band_num)
    array = band.ReadAsArray()

    del dataset
    return array, projection, geotransform


def write_geotiff(
    output_path: str,
    data_array: np.ndarray,
    projection: str,
    geotransform: tuple,
    dtype=gdal.GDT_Int16,
) -> None:
    """Creates a GeoTIFF file from a NumPy array using spatial reference."""
    driver = gdal.GetDriverByName("GTiff")
    height, width = data_array.shape

    out_dataset = driver.Create(output_path, width, height, 1, dtype)
    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(projection)

    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data_array)
    out_band.SetNoDataValue(NODATA_VALUE)

    out_band.FlushCache()
    del out_dataset
