# controllers/preprocessing_ui.py
from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsTask


class PreprocessingUIController:
    """
    UI-контроллер для вкладки 'Подготовка данных'.
    Управляет поведением PreprocessingTab и запускает ГИС-задачи.
    """

    def __init__(self, view, iface):
        self.view = view  # Ссылка на PreprocessingTab
        self.iface = iface

        # Подписываемся на события «компонента» (Вкладки)
        self.view.run_preprocessing_requested.connect(self._on_run_requested)

    def _on_run_requested(self, selected_layers: dict):
        """Реакция на клик по кнопке рассчета индексов"""
        QgsMessageLog.logMessage(
            f"[PreprocessingUI] Юзер запустил расчет для слоев: {selected_layers}",
            "Cajander Matrix",
            Qgis.MessageLevel.Info,
        )

        # Блокируем UI этой конкретной вкладки через её метод
        self.view.set_loading_state(True)
        self.iface.messageBar().pushMessage(
            "Инфо", "Запущен расчет индексов...", level=Qgis.MessageLevel.Info
        )

        # Обертка завершения задачи
        def on_finished(exception):
            self.view.set_loading_state(False)
            if exception:
                self.iface.messageBar().pushMessage(
                    "Ошибка", f"Провал: {exception}", level=Qgis.MessageLevel.Critical
                )
            else:
                self.iface.messageBar().pushMessage(
                    "Успех", "Индексы подготовлены!", level=Qgis.MessageLevel.Success
                )

        # Здесь в будущем будет вызываться ГИС-код, а пока — контролируемая заглушка в QgsTask
        def heavy_gis_job():
            import time

            time.sleep(3)  # Имитация работы ГИС-алгоритма
            return True

        task = QgsTask.fromFunction("Расчет индексов", heavy_gis_job)
        task.taskCompleted.connect(lambda: on_finished(None))
        task.taskTerminated.connect(lambda: on_finished("Прервано"))

        QgsProject.instance().taskManager().addTask(task)
