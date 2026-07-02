"""Сервисный модуль для автоматического поиска, валидации и ленивого чтения растров в NumPy."""

import os
from threading import Lock
from typing import Dict, Optional, Tuple
import numpy as np
from qgis.core import QgsProject, QgsRasterLayer, QgsProcessingException

from ...core.io_handler import read_raster_band
from .registry import REGISTRY, RasterId
from .models import ActiveRaster


class RasterService:
    _instance: Optional["RasterService"] = None
    _lock: Lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RasterService, cls).__new__(cls)
                cls._instance._init_service()
            return cls._instance

    def _init_service(self) -> None:
        self._cache: Dict[RasterId, ActiveRaster] = {}
        self._array_cache: Dict[RasterId, np.ndarray] = {}

    def load_and_validate(self, feedback) -> Tuple[str, tuple, Tuple[int, int]]:
        """
        Ищет растры в проекте QGIS, логирует процесс через feedback
        и проверяет физическое существование файлов.
        """
        self._cache.clear()
        self._array_cache.clear()
        project = QgsProject.instance()

        feedback.pushInfo("🔍 Автоматический поиск и валидация слоев в проекте...")

        for raster_id, meta in REGISTRY.items():
            target_name = meta["qgis_layer_name"]
            layers = project.mapLayersByName(target_name)

            if not layers:
                raise QgsProcessingException(
                    f"Ошибка: В проекте QGIS не найден слой '{target_name}' для константы '{raster_id}'!"
                )

            layer = layers[0]

            # Проверка типа слоя методами QGIS API
            if layer.type() != QgsRasterLayer.RasterLayer:
                raise QgsProcessingException(
                    f"Ошибка: Слой '{target_name}' найден, но он должен быть растровым!"
                )

            if not layer.isValid():
                raise QgsProcessingException(
                    f"Ошибка: Слой '{target_name}' поврежден или не валиден в QGIS!"
                )

            # Проверяем физический путь к файлу источника данных
            source_path = layer.source()
            if not os.path.exists(source_path):
                raise QgsProcessingException(
                    f"Ошибка: Файл растра '{target_name}' отсутствует по пути на диске: {source_path}"
                )

            # Кэшируем успешный результат
            self._cache[raster_id] = ActiveRaster(
                id=raster_id, layer=layer, qgis_name=target_name
            )

            feedback.pushInfo(
                f"   [ОК] Слой '{target_name}' успешно верифицирован. Путь: {source_path}"
            )

        # Читаем метаданные геопривязки и размеры матрицы с эталона
        base_layer = self.get_layer("NDVI_7")
        if not base_layer:
            raise QgsProcessingException(
                "Ошибка: Не удалось извлечь эталонный растр NDVI_7 для геопривязки."
            )

        _, projection, geotransform = read_raster_band(base_layer.source())
        shape = (base_layer.height(), base_layer.width())

        return projection, geotransform, shape

    def get_layer(self, raster_id: RasterId) -> Optional[QgsRasterLayer]:
        return self._cache.get(raster_id).layer if raster_id in self._cache else None

    def get_array(self, raster_id: RasterId) -> np.ndarray:
        """Ленивое чтение файла в NumPy по требованию."""
        if raster_id in self._array_cache:
            return self._array_cache[raster_id]

        layer = self.get_layer(raster_id)
        if not layer:
            raise QgsProcessingException(
                f"Попытка вызвать незарегистрированный растр: {raster_id}"
            )

        array, _, _ = read_raster_band(layer.source())
        self._array_cache[raster_id] = array
        return array

    def clear(self) -> None:
        self._cache.clear()
        self._array_cache.clear()
