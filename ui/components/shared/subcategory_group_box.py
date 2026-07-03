from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


class SubCategoryGroupBox(QWidget):
    """
    Надежный контейнер подкатегории на базе QWidget.
    Использует Grid для создания честного эффекта 'выкушенной' рамки слева.
    """

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        # Главная сетка виджета — управляет наложением заголовка на рамку
        main_grid = QGridLayout(self)
        main_grid.setContentsMargins(0, 5, 0, 0)
        main_grid.setSpacing(0)

        # 1. Заголовок (сажаем в левый верхний угол)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-weight: bold;
            padding: 0 5px;
            background-color: #f0f0f0; /* Цвет фона формы стирает линию под текстом */
        """)

        # 2. Рамка-контейнер для контента
        self.content_frame = QWidget()
        self.content_frame.setStyleSheet("""
            QWidget {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
            }
            QCheckBox {
                border: none; /* Убираем наследование рамки в чекбоксы */
            }
        """)

        # Внутренний слой рамки для размещения чекбоксов
        self.box_layout = QVBoxLayout(self.content_frame)
        self.box_layout.setContentsMargins(12, 15, 12, 10)
        self.box_layout.setSpacing(6)

        # Добавляем в общую сетку: рамка занимает всё пространство
        main_grid.addWidget(self.content_frame, 0, 0, 2, 1)
        # Заголовок накладывается сверху в левый угол (строка 0, колонка 0)
        main_grid.addWidget(self.title_label, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)

        # Делаем небольшой отступ заголовка от левого края рамки
        main_grid.setColumnMinimumWidth(0, 15)

    def setLayout(self, layout):
        """Перенаправляем переданную сетку чекбоксов во внутренний контейнер"""
        if self.content_frame.layout():
            QWidget().setLayout(self.content_frame.layout())
        self.content_frame.setLayout(layout)
