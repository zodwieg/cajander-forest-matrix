# ui/main_dialog.py
import os

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton
from PyQt5.QtCore import pyqtSignal

from .components.tab_classification import ClassificationTab
from .components.tab_preprocessing import PreprocessingTab
from .components.tab_log import LogTab  # Подключаем новый компонент
from ..config.coefficients import save_coefficients
from ..config.coefficients.models import CalibrationCoefficients


class MainBiomeDialog(QDialog):
    # Сигнал для запуска классификации биомов
    run_classification_requested = pyqtSignal(dict, bool)
    # Сигнал для расчета индексов
    run_preprocessing_requested = pyqtSignal(dict)

    def __init__(self, parent, on_param_toggle):
        super().__init__(parent)
        self.setWindowTitle("Классификатор биомов и расчет индексов")
        self.resize(550, 650)

        self.on_param_toggle = on_param_toggle
        self._init_ui()
        self._load_stylesheet()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Главный контейнер вкладок
        self.tabs = QTabWidget()

        # Инициализируем изолированные вкладки-модули
        self.tab_classification = ClassificationTab(self, self.on_param_toggle)
        self.tab_preprocessing = PreprocessingTab(self)
        self.tab_log = LogTab(self)  # Инкапсулированный логгер

        # Добавляем вкладки в виджет
        self.tabs.addTab(self.tab_classification, "1. Классификация биомов")
        self.tabs.addTab(self.tab_preprocessing, "2. Подготовка данных (Индексы)")
        self.tabs.addTab(self.tab_log, "Лог выполнения")

        # Индексы вкладок для быстрой навигации и управления
        self.LOG_TAB_INDEX = self.tabs.indexOf(self.tab_log)

        main_layout.addWidget(self.tabs)

        # Общие нижние кнопки управления
        buttons_layout = QHBoxLayout()

        self.btn_cancel = QPushButton("Закрыть")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_run_classification = QPushButton("Запустить классификацию")
        self.btn_run_classification.setStyleSheet("font-weight: bold;")
        self.btn_run_classification.setDefault(True)
        self.btn_run_classification.clicked.connect(self._handle_classification_apply)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_run_classification)
        buttons_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(buttons_layout)

        # Пробрасываем сигнал из вкладки предобработки наверх к плагину
        self.tab_preprocessing.run_preprocessing_requested.connect(
            self.run_preprocessing_requested.emit
        )

        # Динамически скрываем/показываем нижнюю кнопку "Запустить классификацию",
        # так как на второй вкладке есть своя выделенная кнопка рассчета.
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """Скрывает главную кнопку выполнения, если мы ушли с первой вкладки"""
        self.btn_run_classification.setVisible(index == 0)

    def _handle_classification_apply(self):
        """Забирает стейт из вкладки классификации, упаковывает и отправляет сигнал на расчет"""
        state = self.tab_classification.get_current_state()
        coefs_obj = CalibrationCoefficients(state)

        save_coefficients(coefs_obj)
        should_replace = self.tab_classification.is_replace_raster_checked()

        self.run_classification_requested.emit(coefs_obj.to_dict(), should_replace)

    def set_loading_state(self, is_loading: bool):
        """Универсальный блокировщик UI для тяжелых фоновых задач с автопереключением на логи"""
        # Блокируем кнопки запуска процессов и закрытия окна
        self.btn_run_classification.setEnabled(not is_loading)
        self.btn_cancel.setEnabled(not is_loading)

        # Делегируем внутреннюю блокировку контента рабочим табам
        self.tab_preprocessing.set_loading_state(is_loading)
        if hasattr(self.tab_classification, "set_loading_state"):
            self.tab_classification.set_loading_state(is_loading)

        if is_loading:
            # Сбрасываем и готовим прогресс-бар и текстовое поле внутри таба логов
            self.tab_log.prepare_for_run()

            # Программно переключаем UI на логгер
            self.tabs.setCurrentIndex(self.LOG_TAB_INDEX)

            # Блокируем кликабельность остальных вкладок во время расчета
            for i in range(self.tabs.count()):
                if i != self.LOG_TAB_INDEX:
                    self.tabs.setTabEnabled(i, False)
        else:
            # Скрываем прогресс-бар после завершения
            self.tab_log.finish_run()

            # Разблокируем все вкладки обратно
            for i in range(self.tabs.count()):
                self.tabs.setTabEnabled(i, True)

    def safe_accept(self):
        self.accept()

    def _load_stylesheet(self):
        """Ищет файл style.qss в папке ui/ и применяет его к окну"""
        current_dir = os.path.dirname(__file__)
        qss_path = os.path.join(current_dir, "styles", "style.qss")

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                style_str = f.read()
                self.setStyleSheet(style_str)
        else:
            print(
                f"[MyPlugin] Предупреждение: Файл стилей не найден по пути {qss_path}"
            )

    def set_loading_state(self, is_loading: bool):
        """Управляет доступностью интерфейса и переключением на лог"""
        self.btn_run_classification.setEnabled(not is_loading)
        self.tab_preprocessing.set_loading_state(is_loading)
        self.tab_classification.set_loading_state(is_loading)  # если есть

        if is_loading:
            self.btn_run_classification.setDefault(False)  # Снимаем дефолтность
            self.tabs.setCurrentIndex(self.LOG_TAB_INDEX)
            self.tab_log.prepare_for_run()
            # АВТОМАТИЧЕСКОЕ ПЕРЕКЛЮЧЕНИЕ: переводим пользователя на вкладку лога
            self.tabs.setCurrentIndex(self.LOG_TAB_INDEX)

            # Блокируем остальные вкладки, чтобы пользователь не ушел во время расчета
            for i in range(self.tabs.count()):
                if i != self.LOG_TAB_INDEX:
                    self.tabs.setTabEnabled(i, False)
        else:
            self.tab_log.finish_run()
            self.btn_run_classification.setDefault(True)
            self.tab_log.finish_run()
            # Разблокируем всё обратно
            for i in range(self.tabs.count()):
                self.tabs.setTabEnabled(i, True)
