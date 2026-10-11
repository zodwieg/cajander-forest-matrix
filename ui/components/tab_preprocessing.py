from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QScrollArea,
)
from PyQt5.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel, QgsMessageLog, Qgis

# Импортируем наш новый виджет таблицы
from .raster_inputs_table import RasterInputsTable
from ...config.preprocessing.recipes import RAW_INPUTS_REGISTRY
from .index_selector import IndexSelectorWidget


class PreprocessingTab(QWidget):
    """Главная вкладка подготовки данных с динамической таблицей слоев"""

    # Сигнал теперь должен передавать еще и ID эталонного слоя (str или None)
    run_preprocessing_requested = pyqtSignal(dict, list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # Самый верхний слой вкладки — держит глобальный ScrollArea
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

        # 1. Виджет выбора индексов (Блок 1)
        self.index_selector = IndexSelectorWidget()
        self.index_selector.required_inputs_changed.connect(self._update_needed_inputs)
        self.index_selector.indices_selected_log.connect(self._log_selected_indices)
        main_layout.addWidget(self.index_selector)

        # 2. Блок геометрии и эталонного слоя (Блок 2)
        self.reference_group = QGroupBox("Геометрия и пространственная привязка")
        self.reference_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        ref_layout = QHBoxLayout(self.reference_group)
        ref_layout.setContentsMargins(12, 18, 12, 12)

        ref_label = QLabel("Эталонный растровый слой (сетка и CRS):")
        self.ref_layer_combo = QgsMapLayerComboBox()
        self.ref_layer_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.ref_layer_combo.setAllowEmptyLayer(True)

        ref_layout.addWidget(ref_label)
        ref_layout.addWidget(self.ref_layer_combo, 1)  # Растягиваем комбобокс
        main_layout.addWidget(self.reference_group)

        # 3. Блок динамической таблицы исходных данных (Блок 3)
        self.inputs_group = QGroupBox("Необходимые исходные данные")
        self.inputs_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        table_layout = QVBoxLayout(self.inputs_group)
        table_layout.setContentsMargins(12, 18, 12, 12)

        # Создаем экземпляр нашей новой таблицы
        self.inputs_table = RasterInputsTable()
        table_layout.addWidget(self.inputs_table)
        main_layout.addWidget(self.inputs_group)

        # Инициализируем начальное состояние (скрываем пустые блоки)
        self._update_needed_inputs(set())

        # 4. Блок действий
        actions_group = QGroupBox("Действия")
        actions_layout = QHBoxLayout(actions_group)
        self.btn_calculate_indices = QPushButton("Автоматически рассчитать индексы")
        self.btn_calculate_indices.setStyleSheet("font-weight: bold; padding: 6px;")
        self.btn_calculate_indices.clicked.connect(self._handle_calculate)
        actions_layout.addWidget(self.btn_calculate_indices)
        main_layout.addWidget(actions_group)

        # Финальная пружина
        main_layout.addStretch(1)

        # Устанавливаем собранный контент в глобальный скролл
        global_scroll.setWidget(content_container)

    def _update_needed_inputs(self, needed_inputs: set):
        """Срабатывает при изменении галочек в IndexSelectorWidget"""
        # Если индексы не выбраны — скрываем и эталонный слой, и таблицу
        has_inputs = bool(needed_inputs)
        self.reference_group.setVisible(has_inputs)
        self.inputs_group.setVisible(has_inputs)

        if has_inputs:
            # Наполняем таблицу строками на основе реестра
            self.inputs_table.populate_rows(needed_inputs, RAW_INPUTS_REGISTRY)

    def _log_selected_indices(self, labels: list):
        message = (
            f"Выбраны следующие индексы: {', '.join(labels)}"
            if labels
            else "Отменён выбор всех индексов."
        )
        QgsMessageLog.logMessage(message, "Cajander Matrix", Qgis.Info)

    def _handle_calculate(self):
        active_inputs = self.index_selector.get_selected_product_ids()
        if not active_inputs:
            return

        # Собираем выбранные слои из таблицы
        selected_layers = self.inputs_table.get_selected_layers()

        # Получаем ID эталонного слоя
        ref_layer = self.ref_layer_combo.currentLayer()
        ref_layer_id = ref_layer.id() if ref_layer else ""

        # Эмитим обновленный сигнал (контроллер мы подправим на следующем шаге)
        self.run_preprocessing_requested.emit(
            selected_layers, active_inputs, ref_layer_id
        )

    def set_loading_state(self, is_loading: bool):
        """Блокирует внутренние элементы управления вкладки во время расчета"""
        self.btn_calculate_indices.setEnabled(not is_loading)
        self.ref_layer_combo.setEnabled(not is_loading)

        if hasattr(self.index_selector, "set_loading_state"):
            self.index_selector.set_loading_state(is_loading)
        else:
            self.index_selector.setEnabled(not is_loading)

        # Делегируем блокировку строк самой таблице
        self.inputs_table.set_loading_state(is_loading)
