from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QFileDialog
from PyQt5.QtCore import pyqtSignal
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel


class LayerOrFileSelector(QWidget):
    """Виджет, позволяющий выбрать растр либо из слоев QGIS, либо напрямую с диска."""

    # Сигнал срабатывает, когда пользователь меняет слой или выбирает файл
    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_path = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 1. Стандартный комбобокс слоев QGIS
        self.combo = QgsMapLayerComboBox()
        self.combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.combo.setAllowEmptyLayer(True)
        self.combo.layerChanged.connect(self._on_layer_changed)
        layout.addWidget(self.combo, 1)  # Растягивается

        # 2. Кнопка выбора файла с диска
        self.btn_browse = QToolButton()
        self.btn_browse.setText("...")
        self.btn_browse.setToolTip("Выбрать файл растра с диска")
        self.btn_browse.clicked.connect(self._on_browse_clicked)
        layout.addWidget(self.btn_browse)

    def _on_layer_changed(self):
        # Если пользователь вручную переключил комбобокс на слой, сбрасываем файловый путь
        if self.combo.currentLayer():
            self._file_path = None
        self.data_changed.emit()

    def _on_browse_clicked(self):
        # Открываем стандартный диалог QGIS / Qt для выбора растра
        file_filter = "Геотиффы (*.tif *.tiff);;Все растры (*.img *.png *.jpg *.jpeg);;Все файлы (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите растровый файл", "", file_filter
        )

        if file_path:
            self._file_path = file_path

            # Логика UX: чтобы показать пользователю, что выбран файл,
            # мы временно создаем "виртуальный" слой и добавляем его имя в комбобокс,
            # либо просто временно отключаем комбобокс и пишем имя файла.
            # Самый чистый путь — временно установить пустой слой и поменять тултип.
            self.combo.setLayer(None)
            self.combo.setToolTip(f"Выбран файл: {file_path}")

            # Меняем текст комбобокса, чтобы пользователь видел имя файла
            self.combo.setItemText(
                self.combo.currentIndex(), f"📁 {file_path.split('/')[-1]}"
            )

            self.data_changed.emit()

    def get_value(self):
        """Возвращает либо экземпляр QgsMapLayer, либо строку-путь к файлу, либо None."""
        if self._file_path:
            return self._file_path

        layer = self.combo.currentLayer()
        return layer if layer else None

    def set_value(self, id_or_path: str):
        """Программно устанавливает слой по ID или файл по пути."""
        if not id_or_path:
            return

        import os

        if os.path.exists(id_or_path):
            # Если это путь к файлу
            self._file_path = id_or_path
            self.combo.setLayer(None)
            self.combo.setToolTip(f"Выбран файл: {id_or_path}")
            self.combo.setItemText(
                self.combo.currentIndex(), f"📁 {id_or_path.split('/')[-1]}"
            )
        else:
            # Если это ID слоя QGIS
            from qgis.core import QgsProject

            layer = QgsProject.instance().mapLayer(id_or_path)
            if layer:
                self._file_path = None
                self.combo.setLayer(layer)

    def set_loading_state(self, is_loading: bool):
        """Блокирует виджет во время вычислений."""
        self.combo.setEnabled(not is_loading)
        self.btn_browse.setEnabled(not is_loading)
