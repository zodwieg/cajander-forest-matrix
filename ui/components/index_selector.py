from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QGridLayout,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal, Qt

# Нативный раскрывающийся контейнер верхнего уровня из QGIS
from qgis.gui import QgsCollapsibleGroupBox

# Импортируем рецепты, имена групп и нашу новую палитру цветов
from ...config.preprocessing.recipes import PRODUCTS_RECIPES, GROUP_LABELS, GroupLiteral
from ...config.constants import GROUP_COLORS


class IndexSelectorWidget(QWidget):
    """
    Виджет выбора индексов с железобетонной версткой.
    """

    required_inputs_changed = pyqtSignal(set)
    indices_selected_log = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checkboxes = {}
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(8)

        # --- ГЛОБАЛЬНЫЙ ЧЕКБОКС "ВЫБРАТЬ ВСЕ" ---
        # Размещаем в самом верху, над раскрывающимся блоком. Это стандартный UX.
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(4, 4, 4, 4)

        self.select_all_cb = QCheckBox("Выбрать все доступные индексы")
        self.select_all_cb.setStyleSheet("font-weight: bold; color: #222222;")
        self.select_all_cb.stateChanged.connect(self._on_select_all_toggled)

        top_layout.addWidget(self.select_all_cb)
        top_layout.addStretch()  # Прижимает чекбокс влево
        root_layout.addLayout(top_layout)
        # ----------------------------------------

        # Главная нативная раскрывающаяся панель
        self.main_box = QgsCollapsibleGroupBox("Выбор индексов")
        self.main_box.setCollapsed(False)
        root_layout.addWidget(self.main_box)

        # Внутренний слой главной панели
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(12)
        self.main_box.setLayout(container_layout)

        grid_layouts = {}

        # Строим вложенные группы
        for group_key, group_label in GROUP_LABELS.items():
            bg_color = GROUP_COLORS.get(group_key, "transparent")

            # Стандартный QGroupBox БЕЗ фонового цвета в стилях.
            # Заголовок гарантированно отрендерится на системном фоне формы.
            sub_box = QGroupBox(group_label)
            sub_box.setStyleSheet("QGroupBox { font-weight: bold; border: none; }")

            box_layout = QVBoxLayout(sub_box)
            box_layout.setContentsMargins(
                0, 18, 0, 0
            )  # Отступ сверху, чтобы заголовок не наезжал на плашку

            # Внутренний виджет-подложка, который МЫ КРАСИМ без боли и багов
            bg_widget = QWidget()
            bg_widget.setObjectName("GroupBgWidget")
            bg_widget.setStyleSheet(f"""
                QWidget#GroupBgWidget {{
                    background-color: {bg_color};
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    border-radius: 6px;
                }}
            """)

            # Сетка для чекбоксов (живет внутри цветной подложки)
            grid_layout = QGridLayout(bg_widget)
            grid_layout.setSpacing(10)
            grid_layout.setContentsMargins(14, 10, 14, 10)

            box_layout.addWidget(bg_widget)
            container_layout.addWidget(sub_box)

            grid_layouts[group_key] = grid_layout

        # Распределяем чекбоксы в две колонки
        group_counters = {key: 0 for key in GROUP_LABELS.keys()}

        for raster_id, recipe in PRODUCTS_RECIPES.items():
            group: GroupLiteral = recipe["group"]

            cb = QCheckBox(recipe["label"])
            cb.setProperty("raster_id", raster_id)
            cb.stateChanged.connect(self._on_checkbox_toggled)

            count = group_counters[group]
            row = count // 2
            col = count % 2

            grid_layouts[group].addWidget(cb, row, col, Qt.AlignLeft | Qt.AlignVCenter)
            self._checkboxes[raster_id] = cb
            group_counters[group] += 1

    def _on_checkbox_toggled(self):
        # Управляем состоянием верхнего чекбокса "Выбрать все"
        self.select_all_cb.blockSignals(True)
        checked_count = sum(1 for cb in self._checkboxes.values() if cb.isChecked())

        if checked_count == len(self._checkboxes):
            self.select_all_cb.setCheckState(Qt.Checked)
        elif checked_count == 0:
            self.select_all_cb.setCheckState(Qt.Unchecked)
        else:
            self.select_all_cb.setCheckState(Qt.PartiallyChecked)
        self.select_all_cb.blockSignals(False)

        # Логика сбора данных
        needed_raw_inputs = set()
        selected_labels = []

        for raster_id, cb in self._checkboxes.items():
            if cb.isChecked():
                recipe = PRODUCTS_RECIPES[raster_id]
                needed_raw_inputs.update(recipe["required_inputs"])
                selected_labels.append(recipe["label"])

        self.required_inputs_changed.emit(needed_raw_inputs)
        self.indices_selected_log.emit(selected_labels)

    def _on_select_all_toggled(self, state):
        if state == Qt.PartiallyChecked:
            self.select_all_cb.setCheckState(Qt.Checked)
            state = Qt.Checked

        for cb in self._checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(state == Qt.Checked)
            cb.blockSignals(False)

        self._on_checkbox_toggled()

    def get_selected_product_ids(self) -> list:
        return [r_id for r_id, cb in self._checkboxes.items() if cb.isChecked()]
