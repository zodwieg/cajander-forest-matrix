# controllers/preprocessing_ui.py
import os
from qgis.core import QgsApplication, Qgis, QgsTask
from ..config.preprocessing.model import PreprocessingDependencyResolver
from ..config.preprocessing.service import DataPreparationService


class PreprocessingUIController:
    """UI-контроллер для вкладки 'Подготовка данных'.

    Управляет поведением PreprocessingTab и координирует запуск ГИС-задач.
    """

    def __init__(self, view, iface, layer_manager):
        self.view = view  # Ссылка на PreprocessingTab (Вьюшка)
        self.iface = iface
        # Внедряем менеджер слоев (передадим из MainUIController)
        self.layer_manager = layer_manager

    def _on_selection_changed(self, selected_product_ids: list):
        """Вызывается, когда юзер ставит/снимает галочки с индексов."""
        required_raw_ids = PreprocessingDependencyResolver.resolve_required_inputs(
            selected_product_ids
        )
        self.view.update_required_inputs_table(required_raw_ids)

    def _on_run_requested(
        self, selected_products: list, user_inputs: dict, ref_path: str, output_dir: str
    ):
        """Реакция на клик по кнопке расчета индексов."""
        self.view.set_loading_state(True)
        self._show_message(
            "Инфо", "Запущен процесс подготовки растров...", Qgis.MessageLevel.Info
        )

        prep_service = DataPreparationService(
            reference_raster_path=ref_path, output_dir=output_dir
        )

        # 1. Фоновая функция (выполняется в отдельном потоке)
        # Убираем try/except. Если упадет — упадет штатно в task.taskTerminated
        def heavy_gis_job(task_feedback):
            return prep_service.process(selected_products, user_inputs, task_feedback)

        # 2. Создаем задачу
        task = QgsTask.fromFunction("Подготовка спутниковых данных", heavy_gis_job)

        # 3. Обработчики завершения (выполняются в Главном UI-потоке)
        def on_success():
            self.view.set_loading_state(False)

            # Получаем чистый результат выполнения без кортежей
            result_files = task.returned_values()

            if result_files:
                for file_path in result_files:
                    # Делегируем добавление слоев нашему менеджеру
                    self.layer_manager.add_new_layer(file_path, should_replace=False)

                self._show_message(
                    "Успех",
                    "Все индексы успешно рассчитаны и добавлены в проект!",
                    Qgis.MessageLevel.Success,
                )

        def on_failed():
            self.view.set_loading_state(False)

            # Извлекаем исключение, если оно было выброшено внутри heavy_gis_job
            exception = task.exception()
            error_msg = (
                f"Провал подготовки данных: {exception}"
                if exception
                else "Процесс был прерван пользователем."
            )

            self._show_message("Ошибка", error_msg, Qgis.MessageLevel.Critical)

        # Подписываемся на сигналы таски безопасности ради
        task.taskCompleted.connect(on_success)
        task.taskTerminated.connect(on_failed)

        # Запускаем в менеджере QGIS
        QgsApplication.taskManager().addTask(task)

    def _show_message(self, title: str, text: str, level: Qgis.MessageLevel):
        """Хелпер для вывода сообщений в messageBar QGIS"""
        self.iface.messageBar().pushMessage(title, text, level=level)
