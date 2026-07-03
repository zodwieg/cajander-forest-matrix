from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsRasterLayer, QgsTask
from ..config.preprocessing.model import PreprocessingDependencyResolver
from ..config.preprocessing.service import DataPreparationService
import os


class PreprocessingUIController:
    """UI-контроллер для вкладки 'Подготовка данных'.

    Управляет поведением PreprocessingTab и координирует запуск ГИС-задач.
    """

    def __init__(self, view, iface):
        self.view = view  # Ссылка на PreprocessingTab (Вьюшка)
        self.iface = iface

        # 1. Привязываем события от Вьюшки
        # self.view.product_selection_changed.connect(self._on_selection_changed)
        # self.view.run_preprocessing_requested.connect(self._on_run_requested)

    def _on_selection_changed(self, selected_product_ids: list):
        """Вызывается, когда юзер ставит/снимает галочки с индексов.

        Контроллер пересчитывает зависимости и говорит Вьюшке перерисовать таблицу.
        """
        # Используем наш статический резолвер моделей
        required_raw_ids = PreprocessingDependencyResolver.resolve_required_inputs(
            selected_product_ids
        )

        # Передаем этот список во Вьюшку, чтобы она обновила строки в таблице
        self.view.update_required_inputs_table(required_raw_ids)

    def _on_run_requested(
        self, selected_products: list, user_inputs: dict, ref_path: str, output_dir: str
    ):
        """Реакция на клик по кнопке расчета индексов."""

        self.view.set_loading_state(True)
        self.iface.messageBar().pushMessage(
            "Инфо",
            "Запущен процесс подготовки растров...",
            level=Qgis.MessageLevel.Info,
        )

        # Создаем экземпляр нашего нового сервиса обработки
        # Передаем ему параметры, собранные из UI
        prep_service = DataPreparationService(
            reference_raster_path=ref_path, output_dir=output_dir
        )

        def on_finished(exception, result_files):
            self.view.set_loading_state(False)
            if exception:
                self.iface.messageBar().pushMessage(
                    "Ошибка",
                    f"Провал подготовки данных: {exception}",
                    level=Qgis.MessageLevel.Critical,
                )
            else:
                # Автоматически загружаем созданные растры в проект QGIS, чтобы юзер их увидел
                for file_path in result_files:
                    base_name = os.path.basename(file_path).replace(".tif", "")
                    QgsProject.instance().addMapLayer(
                        QgsRasterLayer(file_path, base_name)
                    )

                self.iface.messageBar().pushMessage(
                    "Успех",
                    "Все индексы успешно рассчитаны и добавлены в проект!",
                    level=Qgis.MessageLevel.Success,
                )

        # Обертка для QgsTask, куда мы передаем управление нашему сервису
        def heavy_gis_job(task_feedback):
            try:
                # Вызываем тяжелую работу внутри сервиса, передавая ему task_feedback для логов
                files = prep_service.process(
                    selected_products, user_inputs, task_feedback
                )
                return True, files
            except Exception as e:
                return False, e

        # Запускаем фоновую задачу QGIS
        task = QgsTask.fromFunction("Подготовка спутниковых данных", heavy_gis_job)

        # Подписываем обработчики завершения
        task.taskCompleted.connect(lambda: on_finished(None, task.returned_values()[1]))
        task.taskTerminated.connect(
            lambda: on_finished("Процесс был прерван пользователем", [])
        )

        QgsProject.instance().taskManager().addTask(task)
