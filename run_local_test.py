# run_local_test.py
import os
import sys

# 1. Добавляем текущую директорию в пути поиска
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# 2. Импортируем наши чистые модули без QGIS
from ui import CajanderJobDto
from services import CajanderProcessingOrchestrator


class MockFeedback:
    """Фейковый логгер, заменяющий QgsProcessingFeedback из QGIS"""

    def pushInfo(self, message: str):
        print(f"[INFO] {message}")

    def reportError(self, error: str, fatal: bool = False):
        print(f"[ERROR] {error}")


def main():
    print("--- ЗАПУСК ЛОКАЛЬНОГО ТЕСТА МАТРИЦЫ КАЯНДЕРА ---")

    # Пути к тестовым файлам (можешь заменить на свои реальные пути)
    # ВНИМАНИЕ: Для теста нужен любой существующий одноканальный TIF файл!
    input_raster = (
        r"C:\Users\zdwia\source\local\qgis_cajander_matrix\test_input_ndvi.tif"
    )
    output_raster = (
        r"C:\Users\zdwia\source\local\qgis_cajander_matrix\test_output_matrix.tif"
    )

    # Если тестового файла нет, создадим лог-предупреждение
    if not os.path.exists(input_raster):
        print(
            f"[⚠️ ВНИМАНИЕ] Положи тестовый растр по пути: {input_raster}\n"
            f"Или укажи в коде run_local_test.py путь к любому своему TIF-файлу."
        )
        return

    # Создаем DTO (как это делал бы data_binder)
    dto = CajanderJobDto(
        input_file_path=input_raster,
        coeff_a=1.5,
        coeff_b=0.8,
        output_path=output_raster,
    )

    # Инициализируем оркестратор и фейковый фидбек
    orchestrator = CajanderProcessingOrchestrator()
    feedback = MockFeedback()

    try:
        # Запуск пайплайна
        orchestrator.run(dto, feedback)
        print("\n[🎉 УСПЕХ] Тест пройден! Файл успешно записан.")
    except Exception as e:
        print("\n[💥 ОШИБКА ВЫПОЛНЕНИЯ ПАЙПЛАЙНА]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
