import sys
import json
import tempfile
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lesson import Lesson
from src.export.text_dump import dump_lesson
from src.verification.snapshops_manager import SnapshotManager, Verbose, StatusLesson


def verify_dump(md_filename: str, verbose: Verbose = Verbose.ERROR) -> bool:
    """Проверяет цикл: markdown -> (деплой) -> дамп с Stepik -> сравнение с исходным markdown."""

    md_path = Path(md_filename)
    if not md_path.exists():
        print(f"Ошибка: файл {md_filename} не найден.")
        return False

    print(f"Начинаем проверку для {md_filename}...")

    # читаем исходный md, чтобы узнать его ID
    try:
        lesson = Lesson()
        with open(md_filename, "r", encoding="utf-8") as f:
            lesson.parse_markdown(f.read())
        lesson_id = lesson.lesson_id
        if not lesson_id:
            print(f"Ошибка: в файле {md_filename} не указан ID урока (lesson: ...).")
            return False
        print(f"ID урока: {lesson_id}")
    except Exception as e:
        print(f"Ошибка при парсинге исходного файла: {e}")
        return False

    # cоздаем временный файл для дампа
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp_file:
        dumped_md_path = tmp_file.name

    # cкачиваем урок со Stepik
    try:
        dump_lesson(lesson_id, filename=dumped_md_path)
    except Exception as e:
        print(f"Ошибка при скачивании урока: {e}")
        Path(dumped_md_path).unlink(missing_ok=True)
        return False

    # используем SnapshotManager для сравнения
    manager = SnapshotManager(verbose=verbose)

    # создаем временную директорию для снапшотов
    with tempfile.TemporaryDirectory() as temp_snapshot_dir:
        # сохраняем оригинальную директорию и временно подменяем
        original_snapshots_dir = manager.snapshots_dir
        manager.snapshots_dir = Path(temp_snapshot_dir)

        try:
            # создаем снапшоты
            manager.create_snapshot(md_filename)  # снапшот для исходного файла
            manager.create_snapshot(dumped_md_path)  # снапшот для скачанного файла

            # проверяем, соответствуют ли файлы своим снапшотам)
            result_orig = manager.check_lesson(md_filename)
            result_dumped = manager.check_lesson(dumped_md_path)

            if result_orig != StatusLesson.PASSED:
                print("Ошибка: исходный файл не соответствует своему снапшоту")
                if verbose < Verbose.DEBUG:
                    print("Запустите с -v для деталей")
                return False

            if result_dumped != StatusLesson.PASSED:
                print("Ошибка: скачанный файл не соответствует своему снапшоту")
                if verbose < Verbose.DEBUG:
                    print("  Запустите с -v для деталей")
                return False

            # сравниваем снапшоты между собой
            snap_orig_path = manager.get_snapshot_path(md_filename)
            snap_dumped_path = manager.get_snapshot_path(dumped_md_path)

            with open(snap_orig_path, "r", encoding="utf-8") as f1:
                snap_orig = json.load(f1)
            with open(snap_dumped_path, "r", encoding="utf-8") as f2:
                snap_dumped = json.load(f2)

            if manager.compare_dict_as_json(snap_orig["steps"], snap_dumped["steps"]):
                print(f"\n✅ УСПЕХ: Исходный и скачанный уроки идентичны!")
                return True
            else:
                print(f"\n❌ ПРОВАЛ: Исходный и скачанный уроки различаются")
                return False

        finally:
            # Восстанавливаем оригинальную директорию
            manager.snapshots_dir = original_snapshots_dir
            Path(dumped_md_path).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Проверка цикла markdown -> Stepik -> markdown."
    )
    parser.add_argument(
        "filename", type=str, help="Путь к исходному markdown-файлу урока."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Подробный вывод различий."
    )
    parser.add_argument(
        "--verbose-level",
        type=str,
        choices=["ERROR", "SUMMARY", "LESSON", "STEP", "DEBUG", "DUMP"],
        default="SUMMARY",
        help="Уровень детализации",
    )
    args = parser.parse_args()

    # преобразуем уровень детализации
    verbose_map = {
        "ERROR": Verbose.ERROR,
        "SUMMARY": Verbose.SUMMARY,
        "LESSON": Verbose.LESSON,
        "STEP": Verbose.STEP,
        "DEBUG": Verbose.DEBUG,
        "DUMP": Verbose.DUMP,
    }

    verbose_level = verbose_map[args.verbose_level]
    if args.verbose:
        verbose_level = Verbose.DEBUG

    success = verify_dump(args.filename, verbose=verbose_level)
    sys.exit(0 if success else 1)
