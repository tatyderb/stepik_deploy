import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from markdownify import markdownify as md
from bs4 import BeautifulSoup, NavigableString, Comment


class BaseExporter:
    """Базовый класс для экспорта шагов в markdown"""

    def __init__(self, step_data, position):
        self.step_data = step_data
        self.position = position
        self.block = step_data.get("block", {})
        self.html = self.block.get("text", "")
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def export(self):
        """Основной метод экспорта"""
        title = self.extract_title()
        self.html = str(self.soup)
        return self.format_output(title)

    def extract_title(self):
        """Извлекает заголовок из HTML"""
        for level in range(1, 7):
            header = self.soup.find(f'h{level}')
            if header:
                title = header.get_text().strip()
                header.decompose()
                return title
        return f"Шаг {self.position}"

    def adjust_header_levels(self, markdown_text, base_level=2):
        """Понижает уровни всех заголовков в markdown тексте"""
        lines = markdown_text.split("\n")
        result_lines = []

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
                    new_level = min(hashes + base_level - 1, 6)
                    result_lines.append("#" * new_level + " " + title)
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)

        return "\n".join(result_lines)

    def format_output(self, title):
        """Форматирует вывод"""
        return f"## {title}\n\n"


class TextDump(BaseExporter):
    """Обработка текстовых шагов"""

    def process_code_blocks(self, soup):
        """Заменяет блоки кода на markdown-формат с языком программирования"""
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if not code:
                continue
            
            lang = None
            if code.has_attr('class'):
                for cls in code['class']:
                    lang = cls[9:]
            
            code_text = code.get_text().strip()
            new_text = f'```{lang or ""}\n{code_text}\n```'
            pre.replace_with(NavigableString(f'\n\n{new_text}\n\n'))
        
        return soup


    def fix_latex(self, text):
        """
        Исправляет LaTeX формулы в тексте после конвертации
        """
        parts = text.split('\\[')
        result = [parts[0]]
        
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

    def format_output(self, title):
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
