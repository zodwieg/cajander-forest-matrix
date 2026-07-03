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
from PyQt5.QtCore import pyqtSignal

# Специальные виджеты QGIS для удобного выбора слоев
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel
from ...config.constants import REQUIRED_INPUTS


class PreprocessingTab(QWidget):
    """
    Вкладка 'Подготовка данных'.
    Позволяет сопоставить исходные растры проекта с требуемыми индексами и запустить пересчет.
    """

    run_preprocessing_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selectors = {}  # Словарь для хранения ссылок на комбобоксы слоев
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Скролл-область на случай мелких экранов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)

        # Динамически строим форму сопоставления слоев
        for row, (key, label_text) in enumerate(REQUIRED_INPUTS):
            label = QLabel(f"{label_text}:")

            layer_combo = QgsMapLayerComboBox()

            # ИСПРАВЛЕННАЯ СТРОКА: используем правильную модель фильтрации растров
            layer_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)

            layer_combo.setAllowEmptyLayer(True)

            grid.addWidget(label, row, 0)
            grid.addWidget(layer_combo, row, 1)

            self._selectors[key] = layer_combo

            scroll.setWidget(container)
            main_layout.addWidget(scroll)

        # Блок управления/запуска рассчета
        actions_group = QGroupBox("Действия")
        actions_layout = QHBoxLayout(actions_group)

        self.btn_calculate_indices = QPushButton(
            "Автоматически рассчитать недостающие индексы"
        )
        self.btn_calculate_indices.setStyleSheet("font-weight: bold; padding: 6px;")
        self.btn_calculate_indices.clicked.connect(self._handle_calculate)

        actions_layout.addWidget(self.btn_calculate_indices)
        main_layout.addWidget(actions_group)

    def _handle_calculate(self):
        """Собирает выбранные пользователем слои и отправляет сигнал в контроллер плагина"""
        selected_layers = {}
        for key, combo in self._selectors.items():
            layer = combo.currentLayer()
            # Передаем id слоя в QGIS или None, если слой не выбран
            selected_layers[key] = layer.id() if layer else None

        # Генерируем сигнал для контроллера (ядра) плагина, где будет выполняться QgsRasterCalculator
        self.run_preprocessing_requested.emit(selected_layers)

    def set_loading_state(self, is_loading: bool):
        """Блокирует интерфейс во время тяжелых расчетов растров"""
        self.btn_calculate_indices.setEnabled(not is_loading)
        for combo in self._selectors.values():
            combo.setEnabled(not is_loading)
