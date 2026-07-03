from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QScrollArea,
)
from PyQt5.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel, QgsMessageLog, Qgis

from ...config.preprocessing.recipes import RAW_INPUTS_REGISTRY
from .index_selector import IndexSelectorWidget


class PreprocessingTab(QWidget):
    """Главная вкладка подготовки данных с единым глобальным скроллбаром"""

    run_preprocessing_requested = pyqtSignal(dict, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selectors = {}
        self._row_widgets = {}
        self._init_ui()

    def _init_ui(self):
        # Самый верхний слой вкладки — просто держит глобальный ScrollArea
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        global_scroll = QScrollArea()
        global_scroll.setWidgetResizable(True)
        global_scroll.setFrameShape(QScrollArea.NoFrame)
        root_layout.addWidget(global_scroll)

        # Контейнер для всего содержимого формы
        content_container = QWidget()
        main_layout = QVBoxLayout(content_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 1. Виджет индексов (теперь раскрывающийся и без внутренних скроллов)
        self.index_selector = IndexSelectorWidget()
        self.index_selector.required_inputs_changed.connect(
            self._update_visible_selectors
        )
        self.index_selector.indices_selected_log.connect(self._log_selected_indices)
        main_layout.addWidget(self.index_selector)

        # 2. Блок выбора сырых растров (без внутреннего скролла)
        self.inputs_group = QGroupBox("Необходимые исходные данные")
        self.inputs_group.setStyleSheet("QGroupBox { font-weight: bold; }")

        grid = QGridLayout(self.inputs_group)
        grid.setSpacing(10)
        grid.setContentsMargins(12, 18, 12, 12)

        for row, (key, meta) in enumerate(RAW_INPUTS_REGISTRY.items()):
            label = QLabel(f"{meta['label']}:")
            layer_combo = QgsMapLayerComboBox()
            layer_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
            layer_combo.setAllowEmptyLayer(True)

            grid.addWidget(label, row, 0, Qt.AlignVCenter)
            grid.addWidget(layer_combo, row, 1)

            self._selectors[key] = layer_combo
            self._row_widgets[key] = (label, layer_combo)

        main_layout.addWidget(self.inputs_group)
        self._update_visible_selectors(set())

        # 3. Блок действий
        actions_group = QGroupBox("Действия")
        actions_layout = QHBoxLayout(actions_group)
        self.btn_calculate_indices = QPushButton("Автоматически рассчитать индексы")
        self.btn_calculate_indices.setStyleSheet("font-weight: bold; padding: 6px;")
        self.btn_calculate_indices.clicked.connect(self._handle_calculate)
        actions_layout.addWidget(self.btn_calculate_indices)

        main_layout.addWidget(actions_group)

        # Добавляем финальную пружину в самый низ контента, чтобы элементы не размазывались по высоте
        main_layout.addStretch(1)

        # Устанавливаем собранный контент в глобальный скролл
        global_scroll.setWidget(content_container)

    def _update_visible_selectors(self, needed_inputs: set):
        self.inputs_group.setVisible(bool(needed_inputs))
        for raw_id, (label, combo) in self._row_widgets.items():
            is_visible = raw_id in needed_inputs
            label.setVisible(is_visible)
            combo.setVisible(is_visible)

    def _log_selected_indices(self, labels: list):
        message = (
            f"Выбраны следующие индексы: {', '.join(labels)}"
            if labels
            else "Отменён выбор всех индексов."
        )
        QgsMessageLog.logMessage(message, "Cajander Matrix", Qgis.Info)

    def _handle_calculate(self):
        selected_layers = {}
        active_inputs = self.index_selector.get_selected_product_ids()
        if not active_inputs:
            return

        for key, combo in self._selectors.items():
            if combo.isVisible():
                layer = combo.currentLayer()
                selected_layers[key] = layer.id() if layer else None

        self.run_preprocessing_requested.emit(selected_layers, active_inputs)
