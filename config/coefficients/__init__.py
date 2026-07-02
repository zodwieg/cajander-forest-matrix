# config/coefficients/__init__.py

# Экспортируем только то, что реально нужно внешнему миру
from .coefficients import get_coefficients, save_coefficients
from .registry import REGISTRY

# Явно объявляем публичный контракт модуля
__all__ = ["get_coefficients", "save_coefficients", "REGISTRY"]
