from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsProcessingFeedback,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,  # Нативный класс контекста
    QgsRasterLayer,
)
import os
from ..ui.calibration_dialog import CalibrationDialog
from ..config import constants as c


class CalibrationController:
    def __init__(self, iface):
        self.iface = iface
        self._dialog = None
        self._current_context = None
        self._current_feedback = None
        self._progress_dialog = None  # Добавим в init для порядка

    def show_dialog(self):
        if self._dialog is None:
            self._dialog = CalibrationDialog(self.iface.mainWindow())
            self._dialog.run_algorithm_requested.connect(self._execute_algorithm)

        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _execute_algorithm(self, coefficients_state: dict):
        """Инициализирует и запускает QgsProcessingAlgorithm в фоновом потоке."""
        algorithm_id = f"{c.PROVIDER_NAME}:{c.ALGO_NAME}"

        algorithm = QgsApplication.processingRegistry().createAlgorithmById(
            algorithm_id
        )
        if not algorithm:
            self.iface.messageBar().pushMessage(
                "Ошибка",
                f"Не удалось найти алгоритм {algorithm_id} в реестре.",
                level=2,
                duration=5,
            )
            return

        params = {
            "COEFFICIENTS": coefficients_state,
            c.PARAM_OUTPUT_RASTER: "TEMPORARY_OUTPUT",
        }

        # Жесткие ссылки для защиты от Garbage Collector
        self._current_context = QgsProcessingContext()
        self._current_feedback = QgsProcessingFeedback()

        task = QgsProcessingAlgRunnerTask(
            algorithm, params, self._current_context, self._current_feedback
        )

        # ХРАНИМ В self! Теперь Python не удалит диалог посреди расчета
        self._progress_dialog = QProgressDialog(
            "Выполняется калибровка алгоритма биомов...", "Отмена", 0, 0, self._dialog
        )
        self._progress_dialog.setWindowTitle("Расчет")
        self._progress_dialog.setWindowModality(Qt.ApplicationModal)

        # Перенаправляем прогресс
        self._current_feedback.progressChanged.connect(
            lambda progress: (
                self._progress_dialog.setValue(int(progress)) if progress > 0 else None
            )
        )

        # Связываем отмену
        self._progress_dialog.canceled.connect(self._current_feedback.cancel)

        self._dialog.set_loading_state(True)

        # ИСПРАВЛЕНО: Убран аргумент `self`, добавлены `success` и `results`
        def on_task_completed(success: bool, results: dict):
            """Слот для обработки завершения задачи алгоритма."""
            # self здесь берется из внешнего контекста класса автоматически!
            self._dialog.set_loading_state(False)

            if self._progress_dialog:
                self._progress_dialog.close()

            if not success:
                if self._current_feedback and self._current_feedback.isCanceled():
                    self.iface.messageBar().pushMessage(
                        "Отмена", "Расчет прерван.", level=1, duration=3
                    )
                else:
                    self.iface.messageBar().pushMessage(
                        "Ошибка",
                        "Ошибка при выполнении алгоритма.",
                        level=2,
                        duration=5,
                    )
                return

            # Результаты теперь приходят прямо в аргумент функции!
            output_path = results.get(c.PARAM_OUTPUT_RASTER)

            if output_path and os.path.exists(output_path):
                layer_name = c.PARAM_OUTPUT_RASTER_NAME
                final_layer = QgsRasterLayer(output_path, layer_name)

                if final_layer.isValid():
                    if os.path.exists(c.DEFAULT_QML_PATH):
                        final_layer.loadNamedStyle(c.DEFAULT_QML_PATH)

                    QgsProject.instance().addMapLayer(final_layer)

                    self.iface.messageBar().pushMessage(
                        "Успех",
                        "Расчет завершен, растр успешно добавлен и стилизован!",
                        level=0,
                        duration=3,
                    )
                else:
                    self.iface.messageBar().pushMessage(
                        "Ошибка",
                        f"Созданный растр невалиден: {output_path}",
                        level=2,
                        duration=5,
                    )

            # Полностью очищаем ссылки
            self._current_context = None
            self._current_feedback = None
            self._progress_dialog = None

        task.executed.connect(on_task_completed)
        QgsApplication.taskManager().addTask(task)
        self._progress_dialog.show()
