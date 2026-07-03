# controllers/main_ui_controller.py
import os
import time
from PyQt5.QtCore import Qt, QMetaObject
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import (
    QgsApplication,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingAlgRunnerTask,
    Qgis,
)

from osgeo import gdal

from ..ui.main_dialog import MainBiomeDialog
from .preprocessing_ui import PreprocessingUIController
from .classification_ui import ClassificationUIController
from ..services.raster_layer_manager import RasterLayerManager  # Наш новый сервис
from ..config import constants as c


class MainUIController:
    """
    Главный оркестратор UI-процессов плагина.
    Координирует работу дочерних контроллеров и запускает ГИС-алгоритмы в фоновых потоках QGIS.
    """

    def __init__(self, iface):
        self.iface = iface
        self._dialog = None
        self.preprocessing_ctrl = None
        self.classification_ctrl = None

        # Внедряем ГИС-сервис как зависимость (Dependency Injection)
        self.layer_manager = RasterLayerManager(self.iface)

        # Инфраструктурные переменные для таск-менеджера QGIS
        self._current_context = None
        self._current_feedback = None
        self._progress_dialog = None

    def show_dialog(self):
        """Инициализация главного окна диалога и дочерних UI-контроллеров"""
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
                view=self._dialog.tab_preprocessing, iface=self.iface
            )
            self._dialog.finished.connect(self._cleanup_dialog)

        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _execute_algorithm(self, coefficients_state: dict, should_replace: bool):
        """Инфраструктурный метод запуска QgsProcessingAlgorithm в QgsTask."""
        algorithm_id = f"{c.PROVIDER_NAME}:{c.ALGO_NAME}"
        algorithm = QgsApplication.processingRegistry().createAlgorithmById(
            algorithm_id
        )

        if not algorithm:
            self.iface.messageBar().pushMessage(
                "Ошибка",
                f"Не удалось найти алгоритм {algorithm_id}.",
                level=Qgis.MessageLevel.Critical,
            )
            return

        # Делегируем сервису подготовку путей к файлам и зачистку старого слоя
        fixed_temp_output = self.layer_manager.generate_output_path(should_replace)
        existing_layer = (
            self.layer_manager.find_layer_by_source(fixed_temp_output)
            if should_replace
            else None
        )

        if should_replace:
            # 1. Сначала ищем и удаляем слой через исправленный менеджер
            existing_layer = self.layer_manager.find_layer_by_source(fixed_temp_output)
            if existing_layer:
                self.layer_manager.release_layer_source(existing_layer)

            # 2. ЖЕСТКИЙ ПРЕДОХРАНИТЕЛЬ: Пробуем физически удалить файл с диска в главном потоке.
            if os.path.exists(fixed_temp_output):
                try:
                    os.remove(fixed_temp_output)
                except OSError:
                    # Если Windows не дает удалить сразу, даем QGIS шанс доуничтожать объекты в памяти
                    for _ in range(3):  # Делаем до 3 коротких попыток с микропаузами
                        QgsApplication.processEvents()
                        time.sleep(0.1)
                        try:
                            os.remove(fixed_temp_output)
                            break  # Если удалилось успешно — выходим из цикла попыток
                        except OSError:
                            continue
                    else:
                        self.iface.messageBar().pushMessage(
                            "Файл заблокирован",
                            "Не удалось перезаписать растр. Удалите слой вручную и повторите расчет.",
                            level=Qgis.Critical,  # В QGIS 3 обычно используется Qgis.Critical или Qgis.MessageLevel.Critical
                            duration=5,
                        )
                        return

        # Конструируем параметры для Processing-движка
        params = {
            "COEFFICIENTS": coefficients_state,
            c.PARAM_OUTPUT_RASTER: fixed_temp_output,
        }

        # Настраиваем контекст, фидбек и диалог прогресс-бара QGIS
        self._current_context = QgsProcessingContext()
        self._current_feedback = QgsProcessingFeedback()
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

        # Переводим SPA-диалог во временный Loading state
        self._dialog.set_loading_state(True)

        # Создаем нативный фоновый таск QGIS
        task = QgsProcessingAlgRunnerTask(
            algorithm, params, self._current_context, self._current_feedback
        )

        # Инкапсулируем логику завершения таски прямо внутри коллбэка
        def on_task_completed(success: bool, results: dict):
            self._dialog.set_loading_state(False)
            if self._progress_dialog:
                self._progress_dialog.close()

            # Обработка сценария Ошибки или Отмены
            if not success:
                if self._current_feedback and self._current_feedback.isCanceled():
                    self.iface.messageBar().pushMessage(
                        "Отмена",
                        "Расчет прерван. Предыдущий слой был удален для перезаписи.",
                        level=Qgis.MessageLevel.Warning,
                        duration=5,
                    )
                else:
                    self.iface.messageBar().pushMessage(
                        "Ошибка",
                        "Ошибка при выполнении алгоритма. Предыдущий слой удален.",
                        level=Qgis.MessageLevel.Critical,
                        duration=5,
                    )

                # Очищаем инфраструктуру и выходим
                self._current_context = None
                self._current_feedback = None
                self._progress_dialog = None
                return

            # Обработка сценария Успеха
            output_path = results.get(c.PARAM_OUTPUT_RASTER)
            if output_path and os.path.exists(output_path):
                # Переменная should_replace подхватывается из родительского метода _execute_algorithm автоматически
                if should_replace:
                    # Случай А: Слой заменяется. Мы удалили старый на старте, а теперь загружаем новый файл
                    self.layer_manager.add_new_layer(output_path, should_replace=True)
                    self.iface.messageBar().pushMessage(
                        "Успех",
                        "Данные слоя успешно перезаписаны и обновлены!",
                        level=Qgis.MessageLevel.Success,
                        duration=3,
                    )
                else:
                    # Случай Б: Загружаем на карту абсолютно новый слой со стилем
                    self.layer_manager.add_new_layer(output_path, should_replace=False)
                    self.iface.messageBar().pushMessage(
                        "Успех",  # Исправлена опечатка в слове "Успех"
                        "Новый растр добавлен на карту!",
                        level=Qgis.MessageLevel.Success,
                        duration=3,
                    )

                # Закрываем диалоговое окно плагина через безопасный стек вызовов PyQt
                if self._dialog:
                    QMetaObject.invokeMethod(
                        self._dialog, "accept", Qt.QueuedConnection
                    )

            # Полная очистка инфраструктурных ссылок
            self._current_context = None
            self._current_feedback = None
            self._progress_dialog = None

        task.executed.connect(on_task_completed)
        QgsApplication.taskManager().addTask(task)
        self._progress_dialog.show()

    def _cleanup_dialog(self):
        self._dialog = None
        self.preprocessing_ctrl = None
        self.classification_ctrl = None
