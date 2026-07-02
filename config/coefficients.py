"""Модуль управления калибровочными коэффициентами биомов (DAL + Mapping)."""

import json
import os

# Пути к файлам калибровки (хранятся в папке со скриптом)
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(CONFIG_DIR, "calibration_storage.json")

# =========================================================================
# ЕДИНЫЙ РЕЕСТР КОЭФФИЦИЕНТОВ (Single Source of Truth)
# Добавлять новые параметры строго сюда. GUI и Сейвер подстроятся сами.
# =========================================================================
REGISTRY = [
    {
        "id": "T_400_SLOPE_MAX",
        "label": "400 Neva - Maximum slope",
        "default": 2.0,
    },
    {
        "id": "T_400_B043_MIN",
        "label": "400 Neva - Minimum March B04",
        "default": 0.8,
    },
    {
        "id": "T_400_NDWI5_MIN",
        "label": "400 Neva - Minimum May NDWI",
        "default": 0.4,
    },
    {
        "id": "T_400_NDRE_MAX",
        "label": "400 Neva - Maximum NDRE",
        "default": 0.3,
    },
]


# =========================================================================
# ДИНАМИЧЕСКИЙ ОБЪЕКТ ДАННЫХ (Аналог Strongly Typed Object / Entity)
# =========================================================================
class CalibrationCoefficients:
    """Объект для десериализации коэффициентов с доступом через точку."""

    def __init__(self, data_dict: dict):
        # Превращаем ключи словаря в полноценные свойства объекта
        for key, value in data_dict.items():
            setattr(self, key, value)


# =========================================================================
# ИНФРАСТРУКТУРА ЧТЕНИЯ / ЗАПИСИ (Реализация репозитория)
# =========================================================================
def load_coefficients() -> CalibrationCoefficients:
    """Загружает сохраненные коэффициенты из JSON или собирает дефолты из реестра."""
    # Собираем словарь дефолтных значений напрямую из REGISTRY
    default_data = {item["id"]: item["default"] for item in REGISTRY}

    if not os.path.exists(CALIBRATION_FILE):
        return CalibrationCoefficients(default_data)

    try:
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            if not isinstance(saved_data, dict):
                return CalibrationCoefficients(default_data)

            # Безопасное слияние (Merge): берем значение из файла,
            # а если добавился новый коэффициент в код — подтягиваем его дефолт
            merged_data = {
                key: saved_data.get(key, default_data[key]) for key in default_data
            }
            return CalibrationCoefficients(merged_data)
    except Exception:
        # Защита "Fail-Safe": при любых проблемах с файлом возвращаем дефолты,
        # чтобы ГИС-инженер не поймал падение QGIS посреди работы
        return CalibrationCoefficients(default_data)


def save_coefficients(coefficients_dict: dict) -> None:
    """Безопасно и атомарно перезаписывает JSON-файл на диске."""
    temp_file = CALIBRATION_FILE + ".tmp"
    try:
        # 1. Пишем транзакционно во временный файл
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(coefficients_dict, f, indent=4, ensure_ascii=False)

        # 2. Атомарно заменяем старый файл новым (защита от повреждения файла при сбое питания)
        if os.path.exists(CALIBRATION_FILE):
            os.remove(CALIBRATION_FILE)
        os.rename(temp_file, CALIBRATION_FILE)
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise RuntimeError(f"Критическая ошибка сохранения калибровки: {e}")
