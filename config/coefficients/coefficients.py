"""Модуль инфраструктуры (DAL + Singleton)."""

import json
import os
from .registry import REGISTRY
from .models import CalibrationCoefficients

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(CONFIG_DIR, "calibration_storage.json")

_current_coefficients = None


def _get_default_data() -> dict:
    default_data = {}
    for biome_id, biome_info in REGISTRY.items():
        default_data[biome_id] = {}
        for group_info in biome_info["groups"].values():
            for param in group_info["parameters"]:
                default_data[biome_id][param["id"]] = param["default"]
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
                merged_data[biome_id] = {
                    param_id: saved_biome_params.get(param_id, default_val)
                    for param_id, default_val in default_biome_params.items()
                }
            return CalibrationCoefficients(merged_data)
    except Exception:
        return CalibrationCoefficients(default_data)


def save_coefficients(coefficients_dict: dict) -> None:
    global _current_coefficients
    temp_file = CALIBRATION_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(coefficients_dict, f, indent=4, ensure_ascii=False)
        if os.path.exists(CALIBRATION_FILE):
            os.remove(CALIBRATION_FILE)
        os.rename(temp_file, CALIBRATION_FILE)
        _current_coefficients = None
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise RuntimeError(f"Ошибка сохранения калибровки: {e}")
