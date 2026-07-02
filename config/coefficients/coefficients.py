"""Модуль инфраструктуры (DAL + Singleton) с поддержкой флагов активности."""

import json
import os
from .registry import REGISTRY, ParamId, BiomeId
from .models import CalibrationCoefficients, ParameterValue

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(CONFIG_DIR, "calibration_storage.json")

_current_coefficients = None


def _get_default_data() -> dict:
    """Генерирует дефолтную структуру, где каждый параметр — это dict."""
    default_data = {}
    for biome_id, biome_info in REGISTRY.items():
        default_data[biome_id] = {}
        for group_info in biome_info["groups"].values():
            for param in group_info["parameters"]:
                # Теперь дефолт тоже содержит флаг активности
                default_data[biome_id][param["id"]] = {
                    "value": param["default"],
                    "is_enabled": True,
                }
    return default_data


def get_coefficients() -> CalibrationCoefficients:
    global _current_coefficients
    if _current_coefficients is None:
        _current_coefficients = load_coefficients()
    return _current_coefficients


def load_coefficients() -> CalibrationCoefficients:
    default_data = _get_default_data()
    if not os.path.exists(CALIBRATION_FILE):
        return CalibrationCoefficients(default_data)
    try:
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            if not isinstance(saved_data, dict):
                return CalibrationCoefficients(default_data)

            merged_data = {}
            for biome_id, default_biome_params in default_data.items():
                saved_biome_params = saved_data.get(biome_id, {})
                merged_data[biome_id] = {}

                for param_id, default_body in default_biome_params.items():
                    saved_body = saved_biome_params.get(param_id)

                    # 1. Если параметра нет в сохраненных — берем дефолт
                    if saved_body is None:
                        merged_data[biome_id][param_id] = default_body
                    # 2. Обратная совместимость: если старый файл хранил просто float
                    elif isinstance(saved_body, (int, float)):
                        merged_data[biome_id][param_id] = {
                            "value": float(saved_body),
                            "is_enabled": True,
                        }
                    # 3. Новый формат: берем значения из файла, подставляя дефолты при пропусках ключей
                    else:
                        merged_data[biome_id][param_id] = {
                            "value": saved_body.get("value", default_body["value"]),
                            "is_enabled": saved_body.get(
                                "is_enabled", default_body["is_enabled"]
                            ),
                        }

            return CalibrationCoefficients(merged_data)
    except Exception:
        return CalibrationCoefficients(default_data)


def save_coefficients(coefficients: CalibrationCoefficients) -> None:
    """Принимает объект CalibrationCoefficients, сериализует и пишет в файл."""
    global _current_coefficients
    temp_file = CALIBRATION_FILE + ".tmp"
    try:
        # Модель сама умеет собирать правильный словарь через .to_dict()
        coefficients_dict = coefficients.to_dict()

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(coefficients_dict, f, indent=4, ensure_ascii=False)
        if os.path.exists(CALIBRATION_FILE):
            os.remove(CALIBRATION_FILE)
        os.rename(temp_file, CALIBRATION_FILE)

        # Обновляем синглтон актуальным объектом, чтобы не перечитывать диск
        _current_coefficients = coefficients
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise RuntimeError(f"Ошибка сохранения калибровки: {e}")


def update_param_state(biome_id: BiomeId, param_id: ParamId, is_enabled: bool) -> None:
    """Метод для контроллера: меняет статус активности параметра и сохраняет."""
    # Получаем текущий синглтон (он гарантированно загружен)
    coefs = get_coefficients()

    try:
        # Пролезаем во внутренности модели и меняем статус
        param_obj = coefs.biome(biome_id).get_raw(param_id)
        param_obj.is_enabled = is_enabled

        # Сбрасываем изменения на диск
        save_coefficients(coefs)
    except AttributeError:
        # Если такого параметра/биома нет в текущей конфигурации
        pass
