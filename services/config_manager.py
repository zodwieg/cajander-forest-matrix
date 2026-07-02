import json
import os
from qgis_cajander_matrix.config import constants as c

# Файл калибровки будет лежать в той же папке, что и этот скрипт
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(CONFIG_DIR, "calibration_storage.json")


def load_calibration_parameters() -> dict:
    """Загружает сохраненные коэффициенты или возвращает дефолтные из constants."""
    default_params = {
        c.PARAM_400_SLOPE_MAX: c.DEFAULT_400_SLOPE_MAX,
        c.PARAM_400_B043_MIN: c.DEFAULT_400_B043_MIN,
        c.PARAM_400_NDWI5_MIN: c.DEFAULT_400_NDWI5_MIN,
        c.PARAM_400_NDRE_MAX: c.DEFAULT_400_NDRE_MAX,
    }

    if not os.path.exists(CALIBRATION_FILE):
        return default_params

    try:
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            # Защита на случай, если файл пустой или поврежден
            if not isinstance(saved_data, dict):
                return default_params

            # Возвращаем сохраненные, а если какого-то ключа нет — берем дефолт
            return {
                key: saved_data.get(key, default_params[key]) for key in default_params
            }
    except Exception:
        # Если файл побился, возвращаем дефолт, чтобы алгоритм не падал
        return default_params


def save_calibration_parameters(new_params: dict) -> None:
    """Безопасно перезаписывает JSON-файл через временный файл-атомарно."""
    temp_file = CALIBRATION_FILE + ".tmp"
    try:
        # Пишем сначала во временный файл
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(new_params, f, indent=4, ensure_ascii=False)

        # Атомарно заменяем старый файл новым (защита от сбоев записи)
        if os.path.exists(CALIBRATION_FILE):
            os.remove(CALIBRATION_FILE)
        os.rename(temp_file, CALIBRATION_FILE)
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise RuntimeError(f"Критическая ошибка сохранения калибровки: {e}")
