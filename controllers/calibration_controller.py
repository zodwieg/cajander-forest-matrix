from PyQt5.QtCore import Qt, QMetaObject
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsProcessingFeedback,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,  # Нативный класс контекста
    QgsRasterLayer,
    QgsMessageLog,
    Qgis,
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
        def handle_param_toggle(param_id: str, is_enabled: bool):
            QgsMessageLog.logMessage(
                f"Параметр {param_id} {'включен' if is_enabled else 'отключен'}",
                "Cajander Matrix",
                Qgis.MessageLevel.Info,
            )
            # Ваша сложная логика записи в сервис/алгоритм
            # self.settings_service.set_param_enabled(param_id, is_enabled)
            # Если нужно, сразу дергаем пересчет
            # self.refresh_preview()

        if self._dialog is None:
            self._dialog = CalibrationDialog(
                parent=self.iface.mainWindow(), on_param_toggle=handle_param_toggle
            )
            self._dialog.run_algorithm_requested.connect(self._execute_algorithm)
            self._dialog.finished.connect(self._cleanup_dialog)
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _cleanup_dialog(self):
        self._state = None
        self._dialog = None

    def _execute_algorithm(self, coefficients_state: dict, should_replace: bool):
        """Инициализирует и запускает QgsProcessingAlgorithm в фоновом потоке."""
        algorithm_id = f"{c.PROVIDER_NAME}:{c.ALGO_NAME}"

        algorithm = QgsApplication.processingRegistry().createAlgorithmById(
            algorithm_id
        )
        if not algorithm:
            self.iface.messageBar().pushMessage(
                "Ошибка", f"Не удалось найти алгоритм {algorithm_id}.", level=2
            )
            return

        import tempfile
        import time

        # Формируем путь к файлу в зависимости от галки
        if should_replace:
            # Стабильное имя для постоянной перезаписи
            filename = f"{c.ALGO_NAME}_validation_output.tif"
        else:
            # Уникальное имя с временной меткой (например, _1719945020.tif), чтобы слои не накладывались на один файл
            filename = f"{c.ALGO_NAME}_{int(time.time())}.tif"

        fixed_temp_output = os.path.join(tempfile.gettempdir(), filename)

        # Поиск существующего слоя нужен только если включен режим замены
        project = QgsProject.instance()
        existing_layer = None

        if should_replace:
            for layer in project.mapLayers().values():
                if (
                    isinstance(layer, QgsRasterLayer)
                    and layer.source() == fixed_temp_output
                ):
                    existing_layer = layer
                    break

            if existing_layer:
                # Освобождаем файл на диске
                existing_layer.setDataSource("", existing_layer.name(), "gdal")

        params = {
            "COEFFICIENTS": coefficients_state,
            c.PARAM_OUTPUT_RASTER: fixed_temp_output,
        }

        # ... (Код инициализации контекста, фидбека и QProgressDialog остается БЕЗ изменений) ...
        self._current_context = QgsProcessingContext()
        self._current_feedback = QgsProcessingFeedback()
        task = QgsProcessingAlgRunnerTask(
            algorithm, params, self._current_context, self._current_feedback
        )
        self._progress_dialog = QProgressDialog(
            "Выполняется калибровка алгоритма биомов...", "Отмена", 0, 0, self._dialog
        )
        self._progress_dialog.setWindowTitle("Расчет")
        self._progress_dialog.setWindowModality(Qt.ApplicationModal)
        self._current_feedback.progressChanged.connect(
            lambda progress: (
                self._progress_dialog.setValue(int(progress)) if progress > 0 else None
            )
        )
        self._progress_dialog.canceled.connect(self._current_feedback.cancel)
        self._dialog.set_loading_state(True)

        def on_task_completed(success: bool, results: dict):
            """Слот для обработки завершения задачи алгоритма."""
            self._dialog.set_loading_state(False)
            if self._progress_dialog:
                self._progress_dialog.close()

            if not success:
                # Возвращаем старый источник, только если мы его затирали
                if (
                    should_replace
                    and existing_layer
                    and os.path.exists(fixed_temp_output)
                ):
                    existing_layer.setDataSource(
                        fixed_temp_output, existing_layer.name(), "gdal"
                    )
                    existing_layer.dataProvider().reloadData()
                    existing_layer.triggerRepaint()

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

            output_path = results.get(c.PARAM_OUTPUT_RASTER)

            if output_path and os.path.exists(output_path):
                # Если мы работаем в режиме замены И старый слой был найден
                if should_replace and existing_layer:
                    existing_layer.setDataSource(
                        output_path, existing_layer.name(), "gdal"
                    )
                    existing_layer.dataProvider().reloadData()
                    existing_layer.triggerRepaint()
                    self.iface.layerTreeView().refreshLayerSymbology(
                        existing_layer.id()
                    )
                    self.iface.messageBar().pushMessage(
                        "Успех", "Данные слоя успешно обновлены!", level=0, duration=3
                    )
                else:
                    # Если это первый запуск ИЛИ режим создания новых слоев (should_replace=False)
                    # Формируем имя слоя: базовое или с отметкой времени для уникальности в легенде
                    display_name = c.PARAM_OUTPUT_RASTER_NAME
                    if not should_replace:
                        import datetime

                        now_str = datetime.datetime.now().strftime("%H:%M:%S")
                        display_name = f"{c.PARAM_OUTPUT_RASTER_NAME} ({now_str})"

                    final_layer = QgsRasterLayer(output_path, display_name)
                    if final_layer.isValid():
                        if os.path.exists(c.DEFAULT_QML_PATH):
                            final_layer.loadNamedStyle(c.DEFAULT_QML_PATH)
                        project.addMapLayer(final_layer)
                        self.iface.messageBar().pushMessage(
                            "Успех",
                            "Новый растр добавлен на карту!",
                            level=0,
                            duration=3,
                        )

                if self._dialog:
                    QMetaObject.invokeMethod(
                        self._dialog, "accept", Qt.QueuedConnection
                    )

            self._current_context = None
            self._current_feedback = None
            self._progress_dialog = None

        task.executed.connect(on_task_completed)
        QgsApplication.taskManager().addTask(task)
        self._progress_dialog.show()
