# config/preprocessing/__init__.py
"""Открытый интерфейс (API) модуля предобработки данных."""

from .recipes import (
    GROUP_LABELS,
    PRODUCTS_RECIPES,
    RAW_INPUTS_REGISTRY,
    GroupLiteral,
    ProductRecipeMeta,
    RawInputId,
    RawInputMeta,
)
from .model import PreprocessingDependencyResolver
from .service import DataPreparationService

# Явно определяем, что доступно при импорте "from config.preprocessing import *"
__all__ = [
    "RawInputId",
    "GroupLiteral",
    "RawInputMeta",
    "ProductRecipeMeta",
    "RAW_INPUTS_REGISTRY",
    "PRODUCTS_RECIPES",
    "GROUP_LABELS",
    "PreprocessingDependencyResolver",
    "DataPreparationService",
]
