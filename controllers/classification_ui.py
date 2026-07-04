from qgis.core import QgsMessageLog, Qgis
from ..config.coefficients.coefficients import update_param_state


class ClassificationUIController:
    """
    UI-контроллер для вкладки 'Классификация биомов'.
    Управляет реакцией на интерактивные изменения параметров и готовит данные для расчета.
    """

    def __init__(self, main_dialog, iface, execute_algorithm_callback):
        self.view = main_dialog.tab_classification
        self.iface = iface
        self.execute_algorithm_callback = execute_algorithm_callback
        main_dialog.run_classification_requested.connect(self._on_run_requested)

    def handle_param_toggle(self, biome_id: str, param_id: str, is_enabled: bool):
        """Слот для обработки включения/выключения чекбоксов параметров"""
        QgsMessageLog.logMessage(
            f"Параметр {param_id} для биома {biome_id} {'включен' if is_enabled else 'отключен'}",
            "Cajander Matrix",
            Qgis.MessageLevel.Info,
        )
        update_param_state(biome_id, param_id, is_enabled)

    def _on_run_requested(self, state_dict: dict, should_replace: bool):
        """Срабатывает, когда пользователь нажимает кнопку 'Запустить классификацию'"""
        self.execute_algorithm_callback(state_dict, should_replace)
