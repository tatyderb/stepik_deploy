import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Type

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from markdownify import markdownify as md
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from src.settings import settings


class BaseExporter:
    """Базовый класс для экспорта шагов в markdown"""

    def __init__(self, step_data: Dict[str, Any], position: int) -> None:
        self.step_data = step_data
        self.position = position
        self.block = step_data.get("block", {})
        self.html = self.block.get("text", "")
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def export(self) -> str:
        """Основной метод экспорта"""
        title, title_level = self.extract_title()
        self.html = str(self.soup)
        return self.format_output(title, title_level)

    def extract_title(self) -> tuple[str, int]:
        """Извлекает заголовок и его уровень из HTML"""
        for level in range(1, 7):
            header = self.soup.find(f'h{level}')
            if header and isinstance(header, Tag):
                title = header.get_text().strip()
                header.decompose()
                return title, level
        return f"Шаг {self.position}", 2

    def adjust_header_levels(self, markdown_text: str, base_level: int = 1) -> str:
        """Понижает уровни всех заголовков в markdown тексте"""
        lines = markdown_text.split("\n")
        result_lines = []
        reduce_by = base_level - 1

        for line in lines:
            if line.startswith('#'):
                hashes = 0
                for char in line:
                    if char == '#':
                        hashes += 1
                    else:
                        break

                if hashes <= 6 and hashes > 0 and (len(line) == hashes or line[hashes] == ' '):
                    title = line[hashes:].lstrip()
                    new_level = min(hashes + reduce_by, 6)
                    result_lines.append("#" * new_level + " " + title)
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)

        return "\n".join(result_lines)

    def fix_latex(self, text: str) -> str:
        """
        Исправляет LaTeX формулы в тексте после конвертации markdownify.
        
        Проблема: markdownify не умеет обрабатывать математические формулы,
        поэтому в результирующем markdown они остаются в исходном LaTeX-формате
        с разделителями \(...\) и \[...\].
        
        Пример исходного текста (после markdownify):
            "Вставка отдельной формулы \(e=mc^2\) в тексте. 
            Отдельно стоящая формула \[y = \sin x\]"
        
        Требуется преобразовать в:
            "Вставка отдельной формулы $e=mc^2$ в тексте.
            Отдельно стоящая формула 
            
            $$y = \sin x$$"
        
        Где:
        - \(...\) → $...$  (inline формулы)
        - \[...\] → \n\n$$...$$\n\n  (display формулы с переносами)
        """
        parts = text.split('\\[')
        result: List[str] = [parts[0]]

        for part in parts[1:]:
            if '\\]' in part:
                before, after = part.split('\\]', 1)
                result.append(f'\n\n$${before}$$\n\n{after}')
            else:
                result.append('\\[' + part)

        text = ''.join(result)
        parts = text.split('\\(')
        result = [parts[0]]

        for part in parts[1:]:
            if '\\)' in part:
                before, after = part.split('\\)', 1)
                result.append(f'${before}${after}')
            else:
                result.append('\\(' + part)

        return ''.join(result)

    def format_output(self, title: str, title_level: int) -> str:
        """Форматирует вывод"""
        return f"{settings.STEP_BEGIN}\n{'#' * title_level} {title}\n\n"


class TextDump(BaseExporter):
    """Обработка текстовых шагов"""

    def process_code_blocks(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Заменяет блоки кода на markdown-формат с языком программирования"""
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if not code or not isinstance(code, Tag):
                continue

            lang: Optional[str] = None
            if code.has_attr('class') and isinstance(code['class'], list):
                for cls in code['class']:
                    if cls.startswith('language-'):
                        lang = cls[9:]
                    elif cls.startswith('lang-'):
                        lang = cls[5:]

            code_text = code.get_text().strip()
            new_text = f'```{lang or ""}\n{code_text}\n```'
            pre.replace_with(NavigableString(f'\n\n{new_text}\n\n'))

        return soup

    def format_output(self, title: str, title_level: int) -> str:
        self.soup = self.process_code_blocks(self.soup)

        text = md(
            str(self.soup),
            heading_style="ATX",
            code_language="",
            code_block="```",
            strip=['script', 'style'],
            autolinks=True,
            escape_underscores=False,
            escape_asterisks=False,
        )

        if text.strip():
            text = self.fix_latex(text)
            text = self.adjust_header_levels(text, base_level=1)

        return f"{settings.STEP_BEGIN} TEXT\n{'#' * title_level} {title}\n\n{text.strip()}\n"


class QuizDump(BaseExporter):
    """Заглушка для QUIZ шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP QUIZ\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class NumberDump(BaseExporter):
    """Обработка численных задач (NUMBER)"""

    def format_output(self, title: str, title_level: int) -> str:

        source: dict[str, any] = self.block.get("source", {})
        options: list[dict[str, str]] = source.get("options", [])

        answers: list[str] = []
        for opt in options:
            answer: str = opt.get("answer", "")
            max_error: str = opt.get("max_error", "0")

            try:
                if max_error and float(max_error) != 0:
                    answers.append(f"ANSWER: {answer} +-{max_error}")
                else:
                    answers.append(f"ANSWER: {answer}")
            except ValueError:
                answers.append(f"ANSWER: {answer}")

        text = md(
            str(self.soup),
            heading_style="ATX",
            code_language="",
            code_block="```",
            strip=['script', 'style'],
            autolinks=True,
            escape_underscores=False,
            escape_asterisks=False,
        )

        if text.strip():
            text = self.fix_latex(text)
            text = self.adjust_header_levels(text, base_level=1)

        result_parts: list[str] = []
        result_parts.append(f"{settings.STEP_BEGIN} NUMBER\n{'#' * title_level} {title}")

        if text.strip():
            result_parts.append("\n" + text.strip())

        if answers:
            result_parts.append("\n" + "\n".join(answers))

        config_lines: list[str] = []

        if "cost" in self.step_data:
            config_lines.append(f"score: {self.step_data['cost']}")

        skip_params = {'options', 'sample_size', 'is_options_feedback'}
        for param_name, param_value in source.items():
            if param_name not in skip_params and param_value is not None:
                if isinstance(param_value, bool):
                    param_value = 'true' if param_value else 'false'
                elif not isinstance(param_value, (str, int, float)):
                    continue
                config_lines.append(f"{param_name}: {param_value}")

        if config_lines:
            result_parts.append("\nCONFIG")
            result_parts.append("\n".join(config_lines))

        return "\n".join(result_parts) + "\n"


class StringDump(BaseExporter):
    """Заглушка для STRING шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP STRING\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class EssayDump(BaseExporter):
    """Заглушка для ESSAY шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP ESSAY\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class SortDump(BaseExporter):
    """Заглушка для SORT шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP SORT\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class TableDump(BaseExporter):
    """Заглушка для TABLE шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP TABLE\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class CodeDump(BaseExporter):
    """Заглушка для TASKINLINE шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP CODE\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


class VideoDump(BaseExporter):
    """Заглушка для VIDEO шагов"""

    def format_output(self, title: str, title_level: int) -> str:
        return f"{settings.STEP_BEGIN} SKIP VIDEO\n{'#' * title_level} {title}\n\nNot implemented yet!\n"


def get_exporter(step_data: Dict[str, Any], position: int) -> BaseExporter:
    """Возвращает подходящий экспортер для шага"""
    block = step_data.get("block", {})
    step_type = block.get("name", "unknown")

    exporters: Dict[str, Type[BaseExporter]] = {
        "text": TextDump,
        "choice": QuizDump,
        "number": NumberDump,
        "string": StringDump,
        "free-answer": EssayDump,
        "sorting": SortDump,
        "table": TableDump,
        "code": CodeDump,
        "video": VideoDump
    }

    exporter_class = exporters.get(step_type, TextDump)
    return exporter_class(step_data, position)


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


def dump_lesson(lesson_id: int, filename: Optional[str] = None) -> None:
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
            step_data: Dict[str, Any] = session.fetch_object("step-source", step_id)

            exporter = get_exporter(step_data, i)
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python text_dump.py LESSON_ID [filename]")
        sys.exit(1)

    lesson_id = int(sys.argv[1])
    filename = sys.argv[2] if len(sys.argv) > 2 else None

    dump_lesson(lesson_id, filename)
