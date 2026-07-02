from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QScrollArea,
    QWidget,
    QLabel,
    QCheckBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

# Импортируем наши модули ядра UI
from .core.form_builder import FormBuilder
from ..config.coefficients import (
    REGISTRY,
    get_coefficients,
    save_coefficients,
)
from ..config.coefficients.models import CalibrationCoefficients


class CalibrationDialog(QDialog):
    run_algorithm_requested = pyqtSignal(dict, bool)

    def __init__(self, parent, on_param_toggle):
        super().__init__(parent)
        self.on_param_toggle = on_param_toggle
        self.setWindowTitle("Калибровка алгоритма биомов (MVP)")
        self.resize(500, 600)
        self._state = {}
        self._load_current_state()
        self._init_ui()
        self._handle_biome_changed()

    def _load_current_state(self):
        """
        Загружает ТЕКУЩИЕ сохраненные коэффициенты из синглтона в локальный State.
        Теперь стейт хранит и значения, и флаги активности параметров.
        """
        coeffs = get_coefficients()

        for biome_id, biome_meta in REGISTRY.items():
            self._state[biome_id] = {}
            biome_coeffs = coeffs.biome(biome_id)

            for group_id, group in biome_meta["groups"].items():
                for param in group["parameters"]:
                    param_id = param["id"]

                    # Извлекаем float-значение (через __getattr__) и статус из модели
                    current_value = getattr(biome_coeffs, param_id, param["default"])
                    is_enabled = (
                        biome_coeffs.is_enabled(param_id)
                        if hasattr(biome_coeffs, "is_enabled")
                        else True
                    )

                    # Сохраняем в стейт структурировано
                    self._state[biome_id][param_id] = {
                        "value": current_value,
                        "is_enabled": is_enabled,
                    }

    def _init_ui(self):
        """Создает статичный каркас окна"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Сверху: Селектор биомов
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Выберите биом:"))

        self.biome_selector = QComboBox()
        for biome_id, biome_meta in REGISTRY.items():
            self.biome_selector.addItem(biome_meta["name"], userData=biome_id)

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

        buttons_layout = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Рассчитать")
        self.btn_save.clicked.connect(self._handle_apply)
        self.btn_save.setDefault(True)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(btn_cancel)
        main_layout.addLayout(buttons_layout)

    def _handle_biome_changed(self):
        """Реактивный хук: очищает экран и просит FormBuilder нарисовать новые поля"""
        biome_id = self.biome_selector.currentData()
        if not biome_id:
            return

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
        """Слот: обновляет значение в локальном стейте при прокрутке любого спинбокса"""
        if param_id in self._state[biome_id]:
            self._state[biome_id][param_id]["value"] = value

    def _update_param_toggle(self, biome_id: str, param_id: str, is_enabled: bool):
        """Слот: обновляет статус активности в стейте и пробрасывает событие в контроллер"""
        if param_id in self._state[biome_id]:
            self._state[biome_id][param_id]["is_enabled"] = is_enabled

        # Вызываем ваш логгер / логику из контроллера
        self.on_param_toggle(biome_id, param_id, is_enabled)

    def _handle_apply(self):
        """Кнопка Запустить расчет: упаковывает стейт в модель, сохраняет и генерирует сигнал"""
        # Создаем полноценный объект модели из локального стейта диалога
        coefs_obj = CalibrationCoefficients(self._state)

        # Сохраняем в JSON на диск и обновляем синглтон
        save_coefficients(coefs_obj)

        should_replace = self.cb_replace_raster.isChecked()

        # Передаем в алгоритм словарь нового формата через .to_dict()
        # { "400": { "SLOPE_MAX": {"value": 2.0, "is_enabled": True} } }
        self.run_algorithm_requested.emit(coefs_obj.to_dict(), should_replace)

    def set_loading_state(self, is_loading: bool):
        """Управляет доступностью кнопки из контроллера во время вычислений"""
        self.btn_save.setEnabled(not is_loading)
        self.biome_selector.setEnabled(not is_loading)

    def safe_accept(self):
        """Потокобезопасный метод для закрытия диалога с успешным кодом."""
        self.accept()
