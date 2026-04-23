from src.logged_requests import setup_logger
from src.stepik_api import StepikSession
from src.auth import read_or_create_auth_data
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def get_lesson_info(session: StepikSession, lesson_id: int) -> tuple[str, List[int]]:
    """
    Получает информацию об уроке: заголовок и список ID шагов
    """
    lesson = session.fetch_object("lesson", lesson_id)
    lesson_title: str = lesson.get("title", "Без названия")
    step_ids: List[int] = lesson.get("steps", [])
    return lesson_title, step_ids


def generate_lesson_header(lesson_title: str, lesson_id: int) -> List[str]:
    """
    Генерирует заголовок урока в markdown формате
    """
    return [f"# {lesson_title}", "", f"lesson: {lesson_id}", ""]


def dump_lesson(lesson_id: int, filename: str | Path | None = None) -> None:
    """
    Скачивает урок со Stepik и сохраняет в markdown файл
    """
    setup_logger()
    read_or_create_auth_data()
    session = StepikSession()

    lesson_title, step_ids = get_lesson_info(session, lesson_id)

    if not step_ids:
        print(f"Урок {lesson_id} не содержит шагов")
        return

    all_markdown: List[str] = generate_lesson_header(lesson_title, lesson_id)

    for i, step_id in enumerate(step_ids, 1):
        try:
            print(f"Обработка шага {i}/{len(step_ids)} (ID: {step_id})...")
            step_data: Dict[str, Any] = session.fetch_object(
                "step-source", step_id)

            from src.dump import BaseExporter

            exporter = BaseExporter.get_exporter(step_data, i)
            step_markdown: str = exporter.export()

            all_markdown.append(step_markdown)

        except Exception as e:
            print(f"Ошибка при обработке шага {step_id}: {e}")
            all_markdown.append(f"## Шаг {i}\n\n[Ошибка экспорта: {e}]\n")

    if not filename:
        filename = f"lesson_{lesson_id}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_markdown))

    print(f"Дамп урока {lesson_id} сохранен в {filename}")
