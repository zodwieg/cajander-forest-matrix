import os

from qgis.core import (
    QgsApplication,
    QgsProcessingContext,
    Qgis,
    QgsTask,
)

from ..ui.main_dialog import MainBiomeDialog
from .preprocessing_ui import PreprocessingUIController
from .classification_ui import ClassificationUIController
from ..services.raster_layer_manager import RasterLayerManager
from ..services.progress_handler import create_processing_progress  # <-- Наш хелпер
from ..config import constants as c
from .controller_log_bridge import ControllerLogBridge


class MainUIController:
    def __init__(self, iface):
        self.iface = iface
        self._dialog = None
        self.preprocessing_ctrl = None
        self.classification_ctrl = None

        self.layer_manager = RasterLayerManager(self.iface)

        # Инфраструктурные переменные
        self._current_context = None
        self._current_feedback = None
        self._progress_dialog = None

    def show_dialog(self):
        """Инициализация главного окна диалога (без изменений)"""
        if self._dialog is None:
            self._dialog = MainBiomeDialog(
                parent=self.iface.mainWindow(),
                on_param_toggle=lambda b_id, p_id, checked: self.classification_ctrl.handle_param_toggle(
                    b_id, p_id, checked
                ),
            )
            self.classification_ctrl = ClassificationUIController(
                main_dialog=self._dialog,
                iface=self.iface,
                execute_algorithm_callback=self._execute_algorithm,
            )
            self.preprocessing_ctrl = PreprocessingUIController(
                view=self._dialog.tab_preprocessing,
                iface=self.iface,
                layer_manager=self.layer_manager,
            )
            self._dialog.finished.connect(self._cleanup_dialog)

        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _execute_algorithm(self, coefficients_state: dict, should_replace: bool):
        """Оркестратор запуска QgsProcessingAlgorithm в фоновом режиме."""
        # 1. Валидация алгоритма
        algorithm_id = f"{c.PROVIDER_NAME}:{c.ALGO_NAME}"
        algorithm = QgsApplication.processingRegistry().createAlgorithmById(
            algorithm_id
        )
        if not algorithm:
            self._show_message(
                "Ошибка",
                f"Не удалось найти алгоритм {algorithm_id}.",
                Qgis.MessageLevel.Critical,
            )
            return

        # 2. Подготовка файловой системы
        output_path = self.layer_manager.generate_output_path(should_replace)
        if should_replace and not self.layer_manager.release_and_delete_source(
            output_path
        ):
            self._show_message(
                "Файл заблокирован",
                "Не удалось перезаписать растр. Удалите слой вручную и повторите расчет.",
                level=Qgis.MessageLevel.Critical,
            )
            return

        # 3. Инициализация UI-прогресса и контекста
        self._current_context = QgsProcessingContext()

        # ИСПРАВЛЕНИЕ: Вместо голого QgsProcessingFeedback создаем наш класс-мост,
        # передавая ему ссылку на вашу вкладку логов
        self._current_feedback = ControllerLogBridge(self._dialog.tab_log)

        # 4. Формирование параметров
        params = {
            "COEFFICIENTS": coefficients_state,
            c.PARAM_OUTPUT_RASTER: output_path,
        }

        # Переводим диалог в состояние загрузки (блокирует поля, переключает на вкладку лога)
        self._dialog.set_loading_state(True)

        # Передаем управление фабрике создания чистой задачи
        task = self._create_runner_task(algorithm, params, should_replace)

        # Отмена задачи связывается стандартным способом
        task.taskTerminated.connect(self._current_feedback.cancel)

        QgsApplication.taskManager().addTask(task)

    def _create_runner_task(
        self, algorithm, params: dict, should_replace: bool
    ) -> QgsTask:
        """Фабричный метод для сборки универсального QgsTask на базе алгоритма."""

        # Сохраняем ссылки на контекст и фидбек в локальные переменные для замыкания
        context = self._current_context
        feedback = self._current_feedback

        # 1. Описываем изолированную функцию, которая выполнится строго в фоне
        def run_processing_in_background(task_instance):
            # Внутри потока используем метод .run()
            # Он вернет кортеж (results_dict, success_bool)
            results, success = algorithm.run(params, context, feedback)
            return {"results": results, "success": success}

        # 2. Создаем стандартный QgsTask из функции
        task = QgsTask.fromFunction(
            f"Расчет: {c.ALGO_DISPLAY_NAME}", run_processing_in_background
        )

        # 3. Метод завершения таски (выполняется строго в Главном UI потоке)
        def on_task_completed():
            # Разблокируем UI нашего плагина (кнопка закрыть станет "Готово")
            self._dialog.set_loading_state(False)

            # ИСПРАВЛЕНИЕ: Проверяем отмену СТРОГО через сам QgsTask.
            if task.isCanceled():
                self._handle_failure()
                self._clear_infrastructure()
                self._show_message(
                    "Отмена",
                    "Расчет прерван пользователем.",
                    level=Qgis.MessageLevel.Warning,
                )
                return

            # Безопасно вытаскиваем то, что вернула функция run_processing_in_background
            task_output = task.returned_values

            # Если задача завершилась аварийно или вернула пустой результат
            if not task_output or not task_output.get("success"):
                self._handle_failure()
                self._clear_infrastructure()
                self._show_message(
                    "Ошибка",
                    "Ошибка при выполнении алгоритма. Проверьте системный лог QGIS.",
                    level=Qgis.MessageLevel.Critical,
                )
                return

            # Если всё ок, извлекаем результаты
            results = task_output.get("results", {})
            output_path = results.get(c.PARAM_OUTPUT_RASTER)

            if output_path and os.path.exists(output_path):
                self.layer_manager.add_new_layer(
                    output_path, should_replace=should_replace
                )
                msg = (
                    "Данные слоя успешно перезаписаны!"
                    if should_replace
                    else "Новый растр добавлен на карту!"
                )
                self._show_message(
                    "Успех", msg, level=Qgis.MessageLevel.Success, duration=3
                )

            self._clear_infrastructure()

        # 4. Подключаем сигналы завершения (без аргументов и без лямбд!)
        task.taskCompleted.connect(on_task_completed)
        task.taskTerminated.connect(on_task_completed)

        return task

    # --- Хелперы для уменьшения дублирования кода (Аналоги приватных методов в C#) ---

    def _show_message(
        self, title: str, text: str, level: Qgis.MessageLevel, duration: int = 5
    ):
        self.iface.messageBar().pushMessage(title, text, level=level, duration=duration)

    def _handle_failure(self):
        if self._current_feedback and self._current_feedback.isCanceled():
            self._show_message(
                "Отмена",
                "Расчет прерван. Предыдущий слой был удален для перезаписи.",
                Qgis.MessageLevel.Warning,
            )
        else:
            self._show_message(
                "Ошибка",
                "Ошибка при выполнении алгоритма. Предыдущий слой удален.",
                Qgis.MessageLevel.Critical,
            )

    def _clear_infrastructure(self):
        self._current_context = None
        self._current_feedback = None
        self._progress_dialog = None

    def _cleanup_dialog(self):
        self._dialog = None
        self.preprocessing_ctrl = None
        self.classification_ctrl = None
