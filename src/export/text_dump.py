import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from html_to_markdown import convert_to_markdown


class BaseExporter:
    """Базовый класс для экспорта шагов в markdown"""

    def __init__(self, step_data, position):
        self.step_data = step_data
        self.position = position
        self.block = step_data.get("block", {})
        self.html = self.block.get("text", "")

    def export(self):
        """Основной метод экспорта"""
        title = self.extract_title()
        return self.format_output(title)

    def extract_title(self):
        """Извлекает заголовок из HTML"""
        title_match = re.search(r"<h([1-6])[^>]*>(.*?)</h\1>", self.html, re.IGNORECASE)
        if title_match:
            title = title_match.group(2).strip()
            # Удаляем заголовок из HTML
            self.html = (
                self.html[: title_match.start()] + self.html[title_match.end() :]
            )
            return title
        return f"Шаг {self.position}"

    def fix_latex(self, text):
        """Исправляет экранированные LaTeX формулы"""
        text = text.replace(r"\(", "$").replace(r"\)", "$")
        text = text.replace(r"\[", "$$").replace(r"\]", "$$")
        text = re.sub(r"\\([=+\-*])", r"\1", text)
        text = text.replace(r"\$", "$")
        return text

    def adjust_header_levels(self, markdown_text, base_level=2):
        """Понижает уровни всех заголовков в markdown тексте"""
        lines = markdown_text.split("\n")
        result_lines = []
        atx_pattern = re.compile(r"^(#{1,6})\s+(.*)$")

        for line in lines:
            atx_match = atx_pattern.match(line)
            if atx_match:
                hashes = atx_match.group(1)
                title = atx_match.group(2)
                current_level = len(hashes)
                new_level = min(current_level + base_level - 1, 6)
                result_lines.append("#" * new_level + " " + title)
            else:
                result_lines.append(line)

        return "\n".join(result_lines)

    def format_output(self, title):
        """Форматирует вывод"""
        return f"## {title}\n\n"


class TextDump(BaseExporter):
    """Обработка текстовых шагов"""

    def format_output(self, title):
        text = convert_to_markdown(self.html, heading_style="atx")
        text = self.fix_latex(text)

        if text.strip():
            text = self.adjust_header_levels(text, base_level=3)

        return f"## {title}\n\n{text.strip()}\n"


class QuizDump(BaseExporter):
    """Заглушка для QUIZ шагов"""

    def format_output(self, title):
        return f"## QUIZ {title}\n"


class NumberDump(BaseExporter):
    """Заглушка для NUMBER шагов"""

    def format_output(self, title):
        return f"## NUMBER {title}\n"


class StringDump(BaseExporter):
    """Заглушка для STRING шагов"""

    def format_output(self, title):
        return f"## STRING {title}\n"


class EssayDump(BaseExporter):
    """Заглушка для ESSAY шагов"""

    def format_output(self, title):
        return f"## ESSAY {title}\n"


class SortDump(BaseExporter):
    """Заглушка для SORT шагов"""

    def format_output(self, title):
        return f"## SORT {title}\n"


class TableDump(BaseExporter):
    """Заглушка для TABLE шагов"""

    def format_output(self, title):
        return f"## TABLE {title}\n"


class CodeDump(BaseExporter):
    """Заглушка для TASKINLINE шагов"""

    def format_output(self, title):
        return f"## TASKINLINE {title}\n\n[Экспорт TASKINLINE шагов в разработке]\n"


def get_exporter(step_data, position):
    """Возвращает подходящий экспортер для шага"""
    block = step_data.get("block", {})
    step_type = block.get("name", "unknown")

    exporters = {
        "text": TextDump,
        "choice": QuizDump,
        "number": NumberDump,
        "string": StringDump,
        "free-answer": EssayDump,
        "sorting": SortDump,
        "table": TableDump,
        "code": CodeDump,
    }

    exporter_class = exporters.get(step_type)
    return exporter_class(step_data, position)


def get_lesson_info(session, lesson_id):
    """
    Получает информацию об уроке: заголовок и список ID шагов
    """
    lesson = session.fetch_object("lesson", lesson_id)
    lesson_title = lesson.get("title", "Без названия")
    step_ids = lesson.get("steps", [])
    return lesson_title, step_ids


def generate_lesson_header(lesson_title, lesson_id):
    """
    Генерирует заголовок урока в markdown формате
    """
    return [f"# {lesson_title}", "", f"lesson: {lesson_id}", ""]


def dump_lesson(lesson_id, filename=None):
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

    all_markdown = generate_lesson_header(lesson_title, lesson_id)

    for i, step_id in enumerate(step_ids, 1):
        try:
            print(f"Обработка шага {i}/{len(step_ids)} (ID: {step_id})...")
            step_data = session.fetch_object("step-source", step_id)

            exporter = get_exporter(step_data, i)
            step_markdown = exporter.export()

            all_markdown.append(step_markdown)

        except Exception as e:
            print(f"Ошибка при обработке шага {step_id}: {e}")
            all_markdown.append(f"## Шаг {i}\n\n[Ошибка экспорта: {e}]\n")

    if not filename:
        filename = f"lesson_{lesson_id}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_markdown))

    print(f"Дамп урока {lesson_id} сохранен в {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python text_dump.py LESSON_ID [filename]")
        sys.exit(1)

    lesson_id = int(sys.argv[1])
    filename = sys.argv[2] if len(sys.argv) > 2 else None

    dump_lesson(lesson_id, filename)
