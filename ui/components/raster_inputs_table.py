from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapLayerComboBox
from .shared.layer_file_selector import LayerOrFileSelector


class RasterInputsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(
            ["Требуемый канал", "Растровый слой / Файл", "Статус"]
        )

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)

    def populate_rows(self, required_raw_ids: set, registry: dict):
        from qgis.core import QgsSettings

        self.setRowCount(0)
        settings = QgsSettings()

        def sort_by_weights(raw_id):
            meta = registry.get(raw_id, {})
            m_weight = meta.get("month_weight", 999)
            c_weight = meta.get("channel_weight", 999)
            return (m_weight, c_weight)

        sorted_raw_ids = sorted(required_raw_ids, key=sort_by_weights)

        for row_idx, raw_id in enumerate(sorted_raw_ids):
            self.insertRow(row_idx)

            meta = registry.get(raw_id, {"label": raw_id})
            label_text = meta.get("label", raw_id)

            # Колонка 0: Название канала
            name_item = QTableWidgetItem(label_text)
            name_item.setData(Qt.UserRole, raw_id)
            self.setItem(row_idx, 0, name_item)

            # Колонка 1: Виджет выбора (Слой + Файл)
            selector = LayerOrFileSelector()

            # Читаем сохраненное значение для этого raw_id (если его нет, вернет пустую строку)
            saved_value = settings.value(
                f"CajanderMatrix/Layers/{raw_id}", "", type=str
            )
            if saved_value:
                selector.set_value(saved_value)

            # Передаем и row_idx, и raw_id в лямбду
            selector.data_changed.connect(
                lambda r=row_idx, k=raw_id: self._on_row_changed(r, k)
            )
            self.setCellWidget(row_idx, 1, selector)

            # Колонка 2: Статус (сразу вызываем валидацию, чтобы подхватить сохраненные данные)
            status_item = QTableWidgetItem()
            status_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row_idx, 2, status_item)
            self._validate_row(row_idx)

    def _on_row_changed(self, row_idx: int, raw_id: str):
        """Срабатывает, когда пользователь меняет значение руками."""
        selector = self.cellWidget(row_idx, 1)
        from qgis.core import QgsSettings

        if selector:
            val = selector.get_value()
            settings = QgsSettings()

            if val is None:
                settings.remove(f"CajanderMatrix/Layers/{raw_id}")
            elif isinstance(val, str):
                settings.setValue(
                    f"CajanderMatrix/Layers/{raw_id}", val
                )  # Сохраняем путь к файлу
            else:
                settings.setValue(
                    f"CajanderMatrix/Layers/{raw_id}", val.id()
                )  # Сохраняем ID слоя

        # После сохранения запускаем валидацию строки
        self._validate_row(row_idx)

    def _validate_row(self, row_idx: int):
        """Ленивая валидация конкретной строки."""
        selector = self.cellWidget(row_idx, 1)
        status_item = self.item(row_idx, 2)

        if not selector or not status_item:
            return

        val = selector.get_value()

        if val is None:
            status_item.setText("⚠️ Выберите растр")
            status_item.setForeground(QColor("#856404"))
            return

        if isinstance(val, str):
            if val.lower().endswith((".tif", ".tiff")):
                status_item.setText("📁 Файл готов")
                status_item.setForeground(QColor("#155724"))
            else:
                status_item.setText("❌ Нужен .TIF файл")
                status_item.setForeground(QColor("#721c24"))
            return

        status_item.setText("✅ Слой готов")
        status_item.setForeground(QColor("#155724"))

    def get_selected_layers(self) -> dict:
        selected_layers = {}
        for row in range(self.rowCount()):
            name_item = self.item(row, 0)
            if not name_item:
                continue

            raw_id = name_item.data(Qt.UserRole)
            selector = self.cellWidget(row, 1)

            if isinstance(selector, LayerOrFileSelector):
                val = selector.get_value()
                if val is None:
                    selected_layers[raw_id] = None
                elif isinstance(val, str):
                    selected_layers[raw_id] = val  # Возвращаем путь к файлу
                else:
                    selected_layers[raw_id] = val.id()  # Возвращаем ID слоя QGIS

        return selected_layers

    def is_valid(self) -> bool:
        """Проверяет, все ли строки заполнены корректно."""
        for row in range(self.rowCount()):
            status_item = self.item(row, 2)
            if status_item and "готов" not in status_item.text():
                return False
        return True

    def set_loading_state(self, is_loading: bool):
        for row in range(self.rowCount()):
            selector = self.cellWidget(row, 1)
            if selector:
                selector.set_loading_state(is_loading)
