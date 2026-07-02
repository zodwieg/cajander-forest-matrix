from typing import Dict, List, Any
from PyQt5.QtCore import Qt  # <--- Вот где на самом деле живет QtCore / Qt!
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QDoubleSpinBox, QLabel
from .data_binder import DataBinder, StateUpdateCallback


class FormBuilder:
    """
    Фабрика динамических компонентов (Dynamic Component Factory).
    Принимает кусок схемы метаданных биома и строит структуру виджетов.
    """

    @staticmethod
    def build_biome_fields(
        groups_meta: Dict[str, Any],
        current_values: Dict[str, Any],
        on_param_change: StateUpdateCallback,
    ) -> List[QGroupBox]:
        """
        Генерирует список виджетов QGroupBox на основе метаданных групп биома.

        :param groups_meta: Словарь "groups" из REGISTRY для выбранного биома
        :param current_values: Локальный стейт текущих значений параметров этого биома
        :param on_param_change: Коллбек формы, вызываемый при мутации инпута
        :return: Список собранных QGroupBox, готовых к вставке в лейаут
        """
        created_groups = []

        # Обходим группы: "terrain", "spectral" и т.д.
        for group_id, group_data in groups_meta.items():

            # 1. Создаем контейнер группы с рамкой и заголовком
            group_box = QGroupBox(group_data["label"])

            # 2. Создаем форму-лейаут для выравнивания полей
            form_layout = QFormLayout(group_box)

            # Настраиваем аккуратные отступы внутри рамки
            form_layout.setSpacing(10)
            form_layout.setContentsMargins(15, 15, 15, 15)

            # Выравниваем лейблы по левому краю для эстетики веба
            form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # 3. Генерируем инпуты для параметров внутри группы
            for param in group_data["parameters"]:
                param_id = param["id"]

                # Создаем подпись
                label = QLabel(param["label"])

                # Создаем числовое поле ввода
                spin_box = QDoubleSpinBox()
                spin_box.setMinimum(param["min"])
                spin_box.setMaximum(param["max"])
                spin_box.setSingleStep(param["step"])

                # Задаем текущее значение: берем из стейта, если нет — из дефолтов
                val = current_values.get(param_id, param["default"])
                spin_box.setValue(val)

                # Растягиваем инпут, чтобы он занимал доступное пространство справа
                spin_box.setSizePolicy(
                    spin_box.sizePolicy().horizontalPolicy(),
                    spin_box.sizePolicy().verticalPolicy(),
                )

                # 4. Прокидываем дата-биндинг через наш DataBinder
                # Передаем контекст: при изменении этого инпута, обнови стейт для param_id
                DataBinder.bind_input(spin_box, param_id, on_change=on_param_change)

                # Добавляем строку "Лейбл - Инпут" в форму
                form_layout.addRow(label, spin_box)

            # Добавляем собранную группу в общий список
            created_groups.append(group_box)

        return created_groups
