from qgis.core import QgsTask, QgsProcessingFeedback, QgsProcessingException
from typing import Dict, List
from ...services.data_preparation.data_preparation_service import DataPreparationService


class PreprocessingTask(QgsTask):
    """Фоновая задача QGIS для безопасного выполнения тяжелых ГИС-вычислений."""

    def __init__(
        self,
        description: str,
        prep_service: DataPreparationService,
        selected_products: List[str],
        resolved_inputs: Dict[str, str],
    ):
        # QgsTask.CanCancel позволяет пользователю нажать "Отмена" в диспетчере задач QGIS
        super().__init__(description, QgsTask.CanCancel)

        self.prep_service = prep_service
        self.selected_products = selected_products
        self.resolved_inputs = resolved_inputs

        # Нативный фидбек QGIS для связи алгоритмов Processing с таском
        self.fx_feedback = QgsProcessingFeedback()
        self.result_files = []
        self.exception_triggered = None

    def run(self) -> bool:
        """Основное тело задачи, выполняемое в фоновом потоке."""
        try:
            # Связываем кнопку "Отмена" из интерфейса QGIS с прерыванием ГИС-скриптов
            self.fx_feedback.progressChanged.connect(self.setProgress)

            # Запускаем наш сервис, передавая ему потокобезопасный фидбек
            self.result_files = self.prep_service.process(
                self.selected_products, self.resolved_inputs, self.fx_feedback
            )
            return True

        except Exception as e:
            self.exception_triggered = e
            return False

    def cancel(self):
        """Вызывается, если пользователь отменил задачу в диспетчере задач QGIS."""
        self.fx_feedback.cancel()
        super().cancel()

    def get_results(self) -> List[str]:
        """Безопасный геттер для получения списка созданных файлов."""
        return self.result_files

    @property
    def task_exception(self):
        """Проброс пойманного исключения наружу."""
        return self.exception_triggered
