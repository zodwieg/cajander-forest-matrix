# services/raster_layer_manager.py
import os
import time
import datetime
import tempfile
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer
from ..config import constants as c

# Импортируем GDAL из стандартной поставки QGIS, чтобы управлять его кэшем
from osgeo import gdal


class RasterLayerManager:
    """
    Низкоуровневый ГИС-сервис.
    Отвечает за генерацию путей, управление источниками данных растров
    в проекте QGIS и применение стилей оформления.
    """

    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()

    def generate_output_path(self, should_replace: bool) -> str:
        """Определяет, куда сохранить выходной растр алгоритма."""
        if should_replace:
            filename = f"{c.ALGO_NAME}_validation_output.tif"
        else:
            filename = f"{c.ALGO_NAME}_{int(time.time())}.tif"
        return os.path.join(tempfile.gettempdir(), filename)

    def find_layer_by_source(self, path: str) -> QgsRasterLayer:
        """Ищет в легенде растровый слой, нормализуя пути Windows."""
        if not path:
            return None

        # Приводим целевой путь к единому системному виду (убираем разницу слэшей)
        target_path = os.path.normpath(path).lower()

        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.source():
                # Нормализуем путь слоя из QGIS
                layer_path = os.path.normpath(layer.source()).lower()
                if layer_path == target_path:
                    return layer
        return None

    def release_layer_source(self, layer: QgsRasterLayer):
        """Полностью удаляет старый слой из QGIS и закрывает дескрипторы файла."""
        if not layer:
            return

        # 1. Запоминаем путь к файлу перед тем, как удалить слой
        file_path = layer.source()

        # 2. Удаляем слой из проекта QGIS (уничтожает связь интерфейса с файлом)
        QgsProject.instance().removeMapLayer(layer.id())

        # 3. Принудительно заставляем GDAL освободить файл, если он существует
        if file_path and os.path.exists(file_path):
            try:
                # Открываем файл в режиме чтения
                dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
                if dataset:
                    # Сбрасываем внутренние буферы этого конкретного датасета
                    dataset.FlushCache()
                    # В Python единственный надежный способ закрыть GDAL-датасет
                    # и освободить дескриптор файла в ОС — это полностью уничтожить ссылку на него.
                    dataset = None
            except Exception:
                pass

        # 4. Прокачиваем очередь событий QGIS, чтобы сборщик мусора (GC) успел всё подчистить
        QgsApplication.processEvents()

    def update_existing_layer(self, layer: QgsRasterLayer, path: str):
        """Обновляет данные растра и заставляет QGIS перерисовать интерфейс легенды."""
        layer.setDataSource(path, layer.name(), "gdal")
        layer.dataProvider().reloadData()
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

    def add_new_layer(self, path: str, should_replace: bool):
        """Создает новый слой в проекте и накладывает QML-стиль (если он есть)."""
        display_name = c.PARAM_OUTPUT_RASTER_NAME
        if not should_replace:
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            display_name = f"{c.PARAM_OUTPUT_RASTER_NAME} ({now_str})"

        final_layer = QgsRasterLayer(path, display_name)
        if final_layer.isValid():
            if os.path.exists(c.DEFAULT_QML_PATH):
                final_layer.loadNamedStyle(c.DEFAULT_QML_PATH)
            self.project.addMapLayer(final_layer)
