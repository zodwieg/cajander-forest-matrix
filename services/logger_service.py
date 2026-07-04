import contextvars
from qgis.core import QgsProcessingFeedback

# Контекстная переменная (аналог Scope в DI контейнерах ASP.NET Core)
# Она изолирована внутри конкретного потока выполнения
_current_feedback: contextvars.ContextVar[QgsProcessingFeedback] = (
    contextvars.ContextVar("current_feedback")
)


class CajanderLogger:
    """Потокобезопасный глобальный сервис логирования"""

    @staticmethod
    def set_context_feedback(feedback: QgsProcessingFeedback):
        """Регистрирует feedback для текущего потока задачи (Аналог DI Scope)"""
        _current_feedback.set(feedback)

    @staticmethod
    def info(message: str):
        """Вывод обычной строчки в лог"""
        try:
            feedback = _current_feedback.get()
            feedback.pushConsoleInfo(message)
        except LookupError:
            # Если вызвали вне контекста задачи (например, в тестах), пишем в консоль
            print(f"[INFO] {message}")

    @staticmethod
    def progress(value: int, text: str = None):
        """Установка процента выполнения и текста (0-100)"""
        try:
            feedback = _current_feedback.get()
            feedback.setProgress(value)
            if text:
                feedback.setProgressText(text)
        except LookupError:
            pass

    @staticmethod
    def is_canceled() -> bool:
        """Проверка, не отменил ли пользователь задачу"""
        try:
            return _current_feedback.get().isCanceled()
        except LookupError:
            return False
