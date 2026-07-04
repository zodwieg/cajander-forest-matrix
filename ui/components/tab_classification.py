# ui/tab_classification.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from qgis.core import QgsSettings

from ..core.form_builder import FormBuilder
from ...config.coefficients import REGISTRY, get_coefficients


class ClassificationTab(QWidget):
    """
    Бывший CalibrationDialog. Теперь это просто виджет-вкладка внутри общего диалога.
    """

    def __init__(self, parent, on_param_toggle):
        super().__init__(parent)
        self.on_param_toggle = on_param_toggle
        self._state = {}
        self._load_current_state()
        self._init_ui()
        self._handle_biome_changed()

    def _load_current_state(self):
        # ... Твой оригинальный код метода _load_current_state без изменений ...
        coeffs = get_coefficients()
        for biome_id, biome_meta in REGISTRY.items():
            self._state[biome_id] = {}
            biome_coeffs = coeffs.biome(biome_id)
            for group_id, group in biome_meta["groups"].items():
                for param in group["parameters"]:
                    param_id = param["id"]
                    current_value = getattr(biome_coeffs, param_id, param["default"])
                    is_enabled = (
                        biome_coeffs.is_enabled(param_id)
                        if hasattr(biome_coeffs, "is_enabled")
                        else True
                    )
                    self._state[biome_id][param_id] = {
                        "value": current_value,
                        "is_enabled": is_enabled,
                    }

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Выберите биом:"))

        self.biome_selector = QComboBox()
        for biome_id, biome_meta in REGISTRY.items():
            self.biome_selector.addItem(biome_meta["name"], userData=biome_id)

        settings = QgsSettings()
        default_biome = list(REGISTRY.keys())[0] if REGISTRY else "400"
        saved_biome_id = settings.value(
            "qgis_cajander_matrix/last_biome", default_biome
        )

        saved_index = self.biome_selector.findData(saved_biome_id)
        if saved_index != -1:
            self.biome_selector.setCurrentIndex(saved_index)

        self.biome_selector.currentIndexChanged.connect(self._handle_biome_changed)
        top_layout.addWidget(self.biome_selector, stretch=1)
        main_layout.addLayout(top_layout)

        self.cb_replace_raster = QCheckBox(
            "Заменять предыдущий растр (Replace previous raster)"
        )
        self.cb_replace_raster.setChecked(True)
        main_layout.addWidget(self.cb_replace_raster)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        main_layout.addWidget(self.scroll_area)

        self.dynamic_container = None

        # Кнопки "Рассчитать" и "Отмена" отсюда УДАЛЕНЫ. Они ушли в основное окно.

    def _handle_biome_changed(self):
        # ... Твой оригинальный код метода _handle_biome_changed без изменений ...
        biome_id = self.biome_selector.currentData()
        if not biome_id:
            return
        QgsSettings().setValue("qgis_cajander_matrix/last_biome", biome_id)

        if self.dynamic_container is not None:
            self.dynamic_container.setParent(None)
            self.dynamic_container.deleteLater()

        self.dynamic_container = QWidget()
        dynamic_layout = QVBoxLayout(self.dynamic_container)
        dynamic_layout.setContentsMargins(0, 0, 0, 0)
        dynamic_layout.setSpacing(10)

        biome_meta = REGISTRY[biome_id]
        current_values = {}
        for pid, pdata in self._state[biome_id].items():
            current_values[pid] = pdata["value"]
            current_values[f"{pid}_enabled"] = pdata["is_enabled"]

        on_param_change = lambda param_id, value: self._update_param_value(
            biome_id, param_id, value
        )
        on_param_toggle = lambda param_id, checked: self._update_param_toggle(
            biome_id, param_id, checked
        )

        group_boxes = FormBuilder.build_biome_fields(
            groups_meta=biome_meta["groups"],
            current_values=current_values,
            on_param_change=on_param_change,
            on_param_toggle=on_param_toggle,
        )
        for box in group_boxes:
            dynamic_layout.addWidget(box)

        dynamic_layout.addStretch()
        self.scroll_area.setWidget(self.dynamic_container)

    def _update_param_value(self, biome_id: str, param_id: str, value: float):
        if param_id in self._state[biome_id]:
            self._state[biome_id][param_id]["value"] = value

    def _update_param_toggle(self, biome_id: str, param_id: str, is_enabled: bool):
        if param_id in self._state[biome_id]:
            self._state[biome_id][param_id]["is_enabled"] = is_enabled
        self.on_param_toggle(biome_id, param_id, is_enabled)

    def get_current_state(self):
        """Публичный метод, чтобы главное окно могло забрать состояние для сохранения"""
        return self._state

    def is_replace_raster_checked(self) -> bool:
        return self.cb_replace_raster.isChecked()

    def set_loading_state(self, is_loading: bool):
        """Блокирует элементы управления вкладки классификации во время расчета"""
        # Блокируем выбор биома
        self.biome_selector.setEnabled(not is_loading)

        # Блокируем чекбокс замены растра
        self.cb_replace_raster.setEnabled(not is_loading)

        # Блокируем всю скролл-область с динамическими полями от FormBuilder
        # Это разом заморозит все внутренние QLineEdit/QDoubleSpinBox/QCheckBox
        self.scroll_area.setEnabled(not is_loading)
