from typing import Dict, List, Any
from PyQt5.QtCore import Qt  # <--- Вот где на самом деле живет QtCore / Qt!
from qgis.PyQt.QtWidgets import (
    QLabel,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QToolButton,
    QGroupBox,
    QWidget,
    QCheckBox,
)
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
        on_param_toggle,
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

                # --- БЛОК 1: Текст и базовые иконки-индикаторы ---
                param_type = str(param.get("type", "")).strip().lower()
                if param_type == "max":
                    icon_active = '<font color="#27ae60">▲</font> '
                elif param_type == "min":
                    icon_active = '<font color="#c0392b">▼</font> '
                else:
                    icon_active = '<font color="#2c3e50">●</font> '

                disabled_color = "#d2d7d9"
                icon_disabled = (
                    f'<font color="{disabled_color}">▼</font> '
                    if param_type == "min"
                    else (
                        f'<font color="{disabled_color}">▲</font> '
                        if param_type == "max"
                        else f'<font color="{disabled_color}">●</font> '
                    )
                )

                # Создаем контейнер для левой части (Чекбокс + Название)
                label_layout = QHBoxLayout()
                label_layout.setContentsMargins(0, 0, 0, 0)
                label_layout.setSpacing(4)

                # Создаем чекбокс активности параметра
                param_checkbox = QCheckBox()
                # Извлекаем начальное состояние (по умолчанию True, если не задано)
                is_active = current_values.get(
                    f"{param_id}_enabled", param.get("enabled_default", True)
                )
                param_checkbox.setChecked(is_active)

                label = QLabel(
                    (icon_active if is_active else icon_disabled) + param["label"]
                )

                label_layout.addWidget(param_checkbox)
                label_layout.addWidget(label)

                # Обертка-виджет для левой части, чтобы засунуть её в QFormLayout
                label_widget = QWidget()
                label_widget.setLayout(label_layout)

                # --- БЛОК 2: Создание поля ввода ---
                spin_box = QDoubleSpinBox()
                spin_box.setMinimum(param["min"])
                spin_box.setMaximum(param["max"])
                spin_box.setSingleStep(param["step"])
                spin_box.setValue(current_values.get(param_id, param["default"]))
                spin_box.setEnabled(is_active)  # блокируем сразу, если выключен

                DataBinder.bind_input(spin_box, param_id, on_change=on_param_change)

                # --- БЛОК 3: Кнопка-подсказка ---
                input_layout = QHBoxLayout()
                input_layout.setContentsMargins(0, 0, 0, 0)
                input_layout.setSpacing(6)
                input_layout.addWidget(spin_box)

                if "comment" in param and param["comment"]:
                    help_btn = QToolButton()
                    help_btn.setText("?")
                    help_btn.setFixedSize(20, 20)
                    # (Стилизацию help_btn оставляем вашу...)
                    html_tooltip = f'<p style="width: 300px; white-space: normal;">{param["comment"]}</p>'
                    help_btn.setToolTip(html_tooltip)
                    input_layout.addWidget(help_btn)
                else:
                    spacer = QWidget()
                    spacer.setFixedSize(20, 20)
                    input_layout.addWidget(spacer)

                # --- БЛОК 4: Логика переключения (События) ---
                def make_toggle_handler(sb, lbl, act_icon, dis_icon, pid, param_label):
                    def handle_toggle(checked):
                        # 1. UI-логика: блокируем/разблокируем спинбокс
                        sb.setEnabled(checked)
                        # 2. UI-логика: меняем цвет стрелочки (теперь используем сохраненный param_label)
                        lbl.setText((act_icon if checked else dis_icon) + param_label)
                        # 3. Бизнес-логика: отправляем событие наружу
                        on_param_toggle(pid, checked)

                    return handle_toggle

                if is_active:
                    label.setText(f"{icon_active}{param['label']}")
                else:
                    label.setText(
                        f"{icon_disabled}<font color='#7f8c8d'>{param['label']}</font>"
                    )

                # Передаем param["label"] седьмым аргументом при подписке на событие
                param_checkbox.toggled.connect(
                    make_toggle_handler(
                        spin_box,
                        label,
                        icon_active,
                        icon_disabled,
                        param_id,
                        param[
                            "label"
                        ],  # <-- Вот здесь мы намертво привязываем текущее имя!
                    )
                )

                # Добавляем в форму: Слева виджет с чекбоксом, справа — спинбокс с кнопкой
                form_layout.addRow(label_widget, input_layout)

            # Добавляем собранную группу в общий список
            created_groups.append(group_box)

        return created_groups
