# services/raster_layer_manager.py
import gc
import os
import time
import datetime
import tempfile
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer
from ..config import constants as c
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

        target_path = os.path.normpath(path).lower()
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.source():
                layer_path = os.path.normpath(layer.source()).lower()
                if layer_path == target_path:
                    return layer
        return None

    def release_and_delete_source(self, path: str) -> bool:
        """
        Полностью удаляет старый слой из QGIS, закрывает дескрипторы GDAL
        и физически стирает файл с диска.
        """
        existing_layer = self.find_layer_by_source(path)

        # 1. Если слой найден в проекте QGIS, удаляем его из легенды
        if existing_layer:
            QgsProject.instance().removeMapLayer(existing_layer.id())
            # ЖЕСТКОЕ ЗАНУЛЕНИЕ: удаляем локальную ссылку, чтобы Python отпустил С++ объект
            existing_layer = None

        # 2. Принудительно заставляем GDAL освободить файл
        if path and os.path.exists(path):
            try:
                dataset = gdal.Open(path, gdal.GA_ReadOnly)
                if dataset:
                    dataset.FlushCache()
                    dataset = None  # Освобождаем дескриптор GDAL
            except Exception:
                pass

        # Форсируем сборку мусора в Python и прокачиваем UI-потоки QGIS
        gc.collect()  # <-- Заставляем Python уничтожить обертки освобожденных объектов
        QgsApplication.processEvents()

        # 3. Пробуем физически удалить файл с диска
        if path and os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError:
                # Наш цикл попыток с микропаузами
                for _ in range(3):
                    gc.collect()  # Пробуем почистить мусор еще раз на всякий случай
                    QgsApplication.processEvents()
                    time.sleep(0.1)
                    try:
                        os.remove(path)
                        return True
                    except OSError:
                        continue
                return False  # Файл так и не поддался

        return True

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
