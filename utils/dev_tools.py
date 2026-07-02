# utils/dev_tools.py
import sys


def reload_project_modules(modules_to_clear: list[str]) -> None:
    """
    Принудительно удаляет модули из кэша Python (sys.modules).
    Позволяет QGIS подтягивать изменения в коде без перезапуска ГИС.
    """
    for module_name in modules_to_clear:
        # 1. Удаляем дочерние модули (например, core.io_handler)
        for key in list(sys.modules.keys()):
            if key.startswith(f"{module_name}."):
                del sys.modules[key]
        # 2. Удаляем сам корневой пакет
        if module_name in sys.modules:
            del sys.modules[module_name]
