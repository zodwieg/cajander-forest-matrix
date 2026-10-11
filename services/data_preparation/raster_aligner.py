import os
from qgis.core import QgsRasterLayer
import processing


class RasterAligner:
    """Выравнивает входные растры по сетке, разрешению и CRS эталона."""

    def __init__(self, reference_path: str, output_dir: str):
        self.ref_path = reference_path
        self.output_dir = output_dir

        ref_layer = QgsRasterLayer(self.ref_path, "ref_meta_temp", "gdal")
        self.ref_crs = ref_layer.crs().authid()
        self.ref_extent = ref_layer.extent()
        self.ref_pixel_x = ref_layer.rasterUnitsPerPixelX()
        self.ref_pixel_y = ref_layer.rasterUnitsPerPixelY()

    def align(self, source_input: str, raw_id: str, feedback) -> str:
        """Репроецирует и ресемплирует растр с фиксацией NoData."""
        output_path = os.path.join(self.output_dir, f"aligned_{raw_id}.tif")

        extent_str = (
            f"{self.ref_extent.xMinimum()},{self.ref_extent.xMaximum()},"
            f"{self.ref_extent.yMinimum()},{self.ref_extent.yMaximum()} [{self.ref_crs}]"
        )

        parameters = {
            "INPUT": source_input,
            "SOURCE_CRS": None,  # Берем исходную CRS из самого файла
            "TARGET_CRS": self.ref_crs,
            "RESAMPLING": 2,
            "TARGET_EXTENT": extent_str,
            "TARGET_RESOLUTION": self.ref_pixel_x,  # Размер пикселя эталона
            "NODATA_SOURCE": None,
            "NODATA_DESTINATION": -9999,  # Устанавливаем NoData для выходного файла
            "DATA_TYPE": 5,  # 5 = Float32
            "OPTIONS": "COMPRESS=LZW",
            "OUTPUT": output_path,
        }

        processing.run("gdal:warpreproject", parameters, feedback=feedback)
        return output_path
