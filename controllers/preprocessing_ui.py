import os
from qgis.core import QgsApplication, Qgis, QgsProject

from ..config.preprocessing.model import PreprocessingDependencyResolver
from ..services.data_preparation.data_preparation_service import DataPreparationService
from .tasks.preprocessing_task import PreprocessingTask

# Импортируем наш новый легковесный сервис загрузки
from ..services.index_layer_loader import IndexLayerLoader


class PreprocessingUIController:
    """UI-контроллер для вкладки 'Подготовка данных'.

    Управляет поведением PreprocessingTab и координирует запуск ГИС-задач.
    """

    def __init__(self, view, iface, layer_manager):
        self.view = view  # Ссылка на PreprocessingTab (Вьюшка)
        self.iface = iface
        self.layer_manager = layer_manager

        # Инициализируем изолированный загрузчик для технических слоев/БД
        self.index_loader = IndexLayerLoader(target_group_name="Рассчитанные индексы")

        # Переподключаем сигнал вьюшки к нашему обновленному слоту
        self.view.run_preprocessing_requested.disconnect()  # На всякий случай сбрасываем старый
        self.view.run_preprocessing_requested.connect(self._on_run_requested)

    def _on_selection_changed(self, selected_product_ids: list):
        """Вызывается, когда юзер ставит/снимает галочки с индексов."""
        required_raw_ids = PreprocessingDependencyResolver.resolve_required_inputs(
            selected_product_ids
        )
        self.view._update_needed_inputs(required_raw_ids)

    def _get_raster_path(self, layer_id_or_path: str) -> str:
        """Вспомогательный метод. Возвращает абсолютный путь к файлу на диске."""
        if not layer_id_or_path:
            return ""

        if os.path.exists(layer_id_or_path):
            return layer_id_or_path

        layer = QgsProject.instance().mapLayer(layer_id_or_path)
        if layer and layer.dataProvider():
            return layer.dataProvider().dataSourceUri()

        return ""

    def _on_run_requested(
        self, user_inputs: dict, selected_products: list, ref_layer_id: str
    ):
        """Реакция на клик по кнопке расчета индексов."""

        # 1. Проверяем ленивую валидацию таблицы перед запуском
        if not self.view.inputs_table.is_valid():
            self._show_message(
                "Предупреждение",
                "Заполните все требуемые каналы корректными растрами перед расчетом!",
                Qgis.MessageLevel.Warning,
            )
            return

        # 2. Получаем и валидируем путь эталонного слоя
        ref_path = self._get_raster_path(ref_layer_id)
        if not ref_path:
            self._show_message(
                "Предупреждение",
                "Не выбран или не найден эталонный растровый слой для геометрии!",
                Qgis.MessageLevel.Warning,
            )
            return

        # 3. Трансформируем пользовательские вводы
        resolved_inputs = {}
        for raw_id, id_or_path in user_inputs.items():
            path = self._get_raster_path(id_or_path)
            if not path:
                self._show_message(
                    "Ошибка",
                    f"Не удалось определить путь для канала: {raw_id}",
                    Qgis.MessageLevel.Critical,
                )
                return
            resolved_inputs[raw_id] = path

        # Настраиваем директорию вывода
        output_dir = os.path.join(os.path.expanduser("~"), "QGIS_Preprocessing_Output")
        os.makedirs(output_dir, exist_ok=True)

        # Блокируем интерфейс формы на время расчетов
        self.view.set_loading_state(True)
        self._show_message(
            "Инфо",
            "Запущен фоновый процесс подготовки растров...",
            Qgis.MessageLevel.Info,
        )

        # Инициализируем наш сервис
        prep_service = DataPreparationService(
            reference_raster_path=ref_path, output_dir=output_dir
        )

        # Создаем экземпляр нашего строгого класса-задачи
        self.active_task = PreprocessingTask(
            description="Подготовка спутниковых данных и расчет индексов",
            prep_service=prep_service,
            selected_products=selected_products,
            resolved_inputs=resolved_inputs,
        )

        # Подключаем именованные методы-слоты вместо вложенных функций
        self.active_task.taskCompleted.connect(self._on_task_success)
        self.active_task.taskTerminated.connect(self._on_task_failed)

        # Отправляем в менеджер задач QGIS
        QgsApplication.taskManager().addTask(self.active_task)

    def _on_task_success(self):
        """Обработчик успешного завершения расчета (выполняется в главном потоке UI)."""
        self.view.set_loading_state(False)

        # Рекомендуемый вариант: таска возвращает словарь {raster_id: file_path}
        # Например: {"NDVI_5": "C:/.../ndvi_5.tif", "TWI": "C:/.../twi.tif"}
        results = self.active_task.get_results()

        if not results:
            return

        loaded_count = 0

        # Перебираем результаты. Поддерживаем как словарь, так и фолбэк на список
        if isinstance(results, dict):
            for raster_id, file_path in results.items():
                try:
                    self.index_loader.load_index_layer(file_path, raster_id)
                    loaded_count += 1
                except Exception as e:
                    self._show_message(
                        "Ошибка импорта",
                        f"Не удалось загрузить индекс {raster_id}: {str(e)}",
                        Qgis.MessageLevel.Critical,
                    )
        else:
            # Фолбэк-вариант: если get_results() пока возвращает список строк,
            # мы пытаемся сопоставить имя файла с ID растра (напр. "ndvi_5.tif" -> "NDVI_5")
            for file_path in results:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                # Ищем подходящий ID из реестра по совпадению с именем файла (регистронезависимо)
                from ..config.rasters.registry import REGISTRY

                raster_id = next(
                    (r_id for r_id in REGISTRY if r_id.lower() == filename.lower()),
                    None,
                )

                if raster_id:
                    self.index_loader.load_index_layer(file_path, raster_id)
                    loaded_count += 1
                else:
                    # Если соответствие не найдено, отдаем в старый layer_manager
                    self.layer_manager.add_new_layer(file_path, should_replace=False)

        if loaded_count > 0:
            self._show_message(
                "Успех",
                f"Рассчитанные слои ({loaded_count} шт.) добавлены в группу 'Рассчитанные индексы'!",
                Qgis.MessageLevel.Success,
            )

    def _on_task_failed(self):
        """Обработчик ошибок или отмены (выполняется в главном потоке UI)."""
        self.view.set_loading_state(False)

        exception = self.active_task.task_exception
        if exception:
            error_msg = f"Провал подготовки данных: {str(exception)}"
            level = Qgis.MessageLevel.Critical
        else:
            error_msg = "Процесс подготовки растров был прерван пользователем."
            level = Qgis.MessageLevel.Warning

        self._show_message("Внимание", error_msg, level)

    def _show_message(self, title: str, text: str, level: Qgis.MessageLevel):
        """Хелпер для вывода сообщений в messageBar QGIS"""
        self.iface.messageBar().pushMessage(title, text, level=level)
