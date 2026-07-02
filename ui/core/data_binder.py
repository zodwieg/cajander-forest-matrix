from typing import Callable, Any
from PyQt5.QtWidgets import QDoubleSpinBox, QWidget

# Тип для нашего коллбека обновления стейта (принимает id_параметра и новое значение)
StateUpdateCallback = Callable[[str, Any], None]


class DataBinder:
    """
    Инфраструктурный сервис для связывания Qt-виджетов с локальным состоянием (State).
    Аналог механизма Data Binding / Control Value Accessor в веб-фреймворках.
    """

    @staticmethod
    def bind_input(
        widget: QWidget, param_id: str, on_change: StateUpdateCallback
    ) -> None:
        """
        Определяет тип виджета, находит нужный Qt-сигнал изменения значения
        и связывает его с коллбеком обновления локального стейта.
        """
        # Проверяем, является ли виджет спинбоксом для чисел с плавающей точкой
        if isinstance(widget, QDoubleSpinBox):
            # valueChanged передает float. Мы используем замыкание (param_id=param_id),
            # чтобы зафиксировать ID параметра в момент подписки.
            widget.valueChanged.connect(
                lambda value, p_id=param_id: on_change(p_id, value)
            )

        # Сюда в будущем легко добавить другие типы инпутов:
        # elif isinstance(widget, QCheckBox):
        #     widget.stateChanged.connect(lambda state, p_id=param_id: on_change(p_id, bool(state)))
        # elif isinstance(widget, QComboBox):
        #     widget.currentIndexChanged.connect(...)

        else:
            raise TypeError(f"DataBinder: Неподдерживаемый тип виджета {type(widget)}")
