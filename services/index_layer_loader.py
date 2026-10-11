import os
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeGroup
from ..config.rasters.registry import REGISTRY, RasterId


class IndexLayerLoader:
    """Сервис для быстрой загрузки расчетных растров в интерфейс QGIS

    без изменения их исходного (дефолтного) визуального стиля.
    """

    def __init__(self, target_group_name: str = "Рассчитанные индексы"):
        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.target_group_name = target_group_name

    def load_index_layer(self, file_path: str, raster_id: RasterId) -> QgsRasterLayer:
        """Загружает растр, именует строго по qgis_layer_name и помещает в группу."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл растра не найден: {file_path}")

        if raster_id not in REGISTRY:
            raise KeyError(f"ID '{raster_id}' отсутствует в registry.py")

        # Берем техническое имя, которое строго ожидает основной алгоритм
        layer_name = REGISTRY[raster_id]["qgis_layer_name"]

        # Создаем слой с дефолтным стилем отображения QGIS
        raster_layer = QgsRasterLayer(file_path, layer_name)
        if not raster_layer.isValid():
            raise ValueError(f"QGIS не смог прочитать файл растра: {file_path}")

        # Защита базы данных: удаляем старый слой с этим именем перед добавлением нового
        self._remove_old_layer_if_exists(layer_name)

        # Регистрируем слой в проекте (False отключает авто-добавление в корень дерева)
        self.project.addMapLayer(raster_layer, False)

        # Добавляем строго в изолированную техническую группу
        target_group = self._get_or_create_group()
        target_group.addLayer(raster_layer)

        return raster_layer

    def _get_or_create_group(self) -> QgsLayerTreeGroup:
        """Находит или создает техническую группу в панели слоев."""
        group = self.root.findGroup(self.target_group_name)
        if not group:
            group = self.root.addGroup(self.target_group_name)
        return group

    def _remove_old_layer_if_exists(self, layer_name: str):
        """Удаляет существующие слои с таким же именем во избежание дубликатов."""
        existing_layers = self.project.mapLayersByName(layer_name)
        for layer in existing_layers:
            self.project.removeMapLayer(layer.id())
