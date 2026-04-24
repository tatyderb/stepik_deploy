import sys
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional, Dict, Any, List, Type
from markdownify import markdownify as md
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import read_or_create_auth_data
from src.stepik_api import StepikSession
from src.logged_requests import setup_logger
from src.settings import settings
import click


class BaseExporter(ABC):
    """Базовый класс для экспорта шагов в markdown"""

    def __init__(self, step_data: Dict[str, Any], position: int) -> None:
        self.step_data = step_data
        self.position = position
        self.block = step_data.get("block", {})
        self.step_type = self.block.get("name", "unknown").upper()
        self.html = self.block.get("text", "")
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.set_type()

    def set_type(self):
        """Здесь можно установить другое название типа для markdown"""
        self.step_type = self.block.get("name", "unknown").upper()

    def export(self) -> str:
        """Окончательное преобразование json в markdown"""
        # при дампе: строго новый формат начала шага
        return f"{settings.STEP_BEGIN} {self.step_type}\n\n{self.format_output()}\n"

    @abstractmethod
    def format_output(self) -> str:
        """Представление шага в формате markdown."""
        pass

    @classmethod
    def process_code_blocks(cls, soup: BeautifulSoup) -> BeautifulSoup:
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

    @classmethod
    def fix_latex(cls, text: str) -> str:
        r"""
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

    @classmethod
    def html_to_markdown(cls, soup: BeautifulSoup, has_codeblock: bool = True, has_latex: bool = True):
        """Преобразует текст из html в mardown с корректным преобразованием вставок кода и математических формул.
        has_codeblock: вставлять ли название языка в блок кода для подсветки синтаксиса
        has_latex: могут ли быть в тексте математические формулы
        """
        if has_codeblock:
            soup = cls.process_code_blocks(soup)

        text = md(
            str(soup),
            heading_style="ATX",
            code_language="",
            code_block="```",
            strip=['script', 'style'],
            autolinks=True,
            escape_underscores=False,
            escape_asterisks=False,
        )

        if has_latex:
            text = cls.fix_latex(text)

        return text

    def dump_config(self, source: dict, step_data: dict) -> List[str]:
        """
        Общий метод для дампа конфигурации шага.
        TODO: писать только то, что отличается от настроек типа.
        """
        config_lines: List[str] = []

        if "cost" in step_data:
            config_lines.append(f"score: {step_data['cost']}")

        allowed_params = {
            'text': [],
            'number': [],
            'string': ['case_sensitive', 'use_re'],
            'choice': [],
            'matching': ['shuffle', 'html'],
            'sorting': ['html'],
            'table': ['allow_multiple', 'shuffle_columns', 'accept_any_answer', 'shuffle_rows'],
            'free-answer': ['is_attachments_enabled', 'is_html_enabled', 'manual_scoring'],
            'code': ['lang', 'mode', 'open_tests', 'checker']
        }

        step_type = self.block.get('name', 'unknown')
        allowed = allowed_params.get(step_type, [])

        for param_name, param_value in source.items():
            if param_name in allowed and isinstance(param_value, (bool, str, int, float)):
                config_lines.append(f"{param_name}: {param_value}")

        return config_lines


class BaseNotImplementedExporter(BaseExporter):
    def export(self) -> str:
        """Окончательное преобразование json в markdown"""
        # заглушка для нереализованных типов
        return f"{settings.STEP_BEGIN} SKIP {self.step_type}\n\nNot implemented yet!\n"

    def format_output(self) -> str:
        pass


class TextDump(BaseExporter):
    """Обработка текстовых шагов"""

    def format_output(self) -> str:
        text = self.html_to_markdown(self.soup)
        return text.strip()


class QuizDump(BaseExporter):
    """Обработка QUIZ шагов (выбор одного или нескольких вариантов)"""

    def set_type(self):
        self.step_type = "QUIZ"

    def format_output(self) -> str:
        """
        Из
        {
          "block": {
            "name": "choice",
            "text": "текст условия задачи в html",
            "source": {
              "options": [
                {"is_correct": true, "text": "<p>5</p>"},
                {"is_correct": false, "text": "<p>-5</p>"},
                {"is_correct": false, "text": "<p>0</p>"},
                {"is_correct": false, "text": "<p>55</p>"}
              ],
              "is_multiple_choice": false,
              "is_html_enabled": true
            }
          },
        }
        возвращаем в виде строки
        текст условия задачи в html

        A. 5
        B. -5
        C. 0
        D. 55

        ANSWER: A

        :return: шаг в формате markdown
        """
        source: dict[str, any] = self.block.get("source", {})
        options: list[dict[str, any]] = source.get("options", [])
        is_html_enabled = source.get("is_html_enabled", False)

        variants = []
        for idx, opt in enumerate(options):
            opt_text = opt.get("text", "")
            letter = chr(ord('A') + idx)

            if is_html_enabled and opt_text:
                soup = BeautifulSoup(opt_text, 'html.parser')
                processed_text = self.html_to_markdown(
                    soup, 
                    has_codeblock=True, 
                    has_latex=True
                ).strip()
            else:
                processed_text = BeautifulSoup(opt_text, 'html.parser').get_text().strip()

            variants.append(f"{letter}. {processed_text}")
        
        correct = []
        for idx, opt in enumerate(options):
            if opt.get("is_correct", False):
                correct.append(chr(ord('A') + idx))
        
        answers = [f"ANSWER: {', '.join(correct)}"]
        
        result_parts: list[str] = [
            self.html_to_markdown(self.soup),
            "",
            *variants,
            "",
            *answers,
            "",
            "CONFIG",
            *self.dump_config(source, self.step_data)
        ]
        
        return "\n".join(result_parts) + "\n"


class NumberDump(BaseExporter):
    """Обработка численных задач (NUMBER)"""

    def format_output(self) -> str:
        """
        Из
        {
          "block": {
            "name": "number",
            "text": "текст условия задачи в html",
            "source": {
              "options": [{
                  "answer": "4.0",
                  "max_error": "0.0"
                },
                {
                  "answer": "-8.5",
                  "max_error": "0.1"
                }],
            },
          },
        }
        возвращаем в виде строки
        текст условия задачи в markdown

        ANSWER: 4.0
        ANSWER: -8.5 +- 0.1

        :return: шаг в виде строки в формате markdown
        """

        source: dict[str, any] = self.block.get("source", {})
        options: list[dict[str, str]] = source.get("options", [])

        self.soup = self.process_code_blocks(self.soup)

        # Правильных ответов может быть несколько
        answers: list[str] = []
        for opt in options:
            answer: str = opt["answer"]
            max_error: str = opt.get("max_error", "0")

            try:
                if max_error and float(max_error) != 0:
                    answers.append(f"ANSWER: {answer} +-{max_error}")
                else:
                    answers.append(f"ANSWER: {answer}")
            except ValueError:
                raise ValueError(
                    f"WARNING: Некорректное значение max_error='{max_error}' для ответа '{answer}' в шаге {self.position}"
                )

        result_parts: list[str] = [
            self.html_to_markdown(self.soup),
            "",
            *answers,
            "",
            "CONFIG",
            *self.dump_config(source, self.step_data)
        ]
        return "\n".join(result_parts) + "\n"


class StringDump(BaseExporter):
    """Обработка STRING шагов"""

    def format_output(self) -> str:
        """
        Преобразует json в markdown
        {
          "block": {
            "name": "string",
            "text": "<h2>Регулярные выражения</h2>\n<p>Напишите север или юг</p>",
            "source": {
              "pattern": "север|юг",
              "use_re": true,
              "match_substring": false,
              "case_sensitive": false,
              "is_text_disabled": false,
              "is_file_disabled": true
            }
          },
        }
        в
        ##  Регулярные выражения
        Напишите север или юг
        ANSWER: север|юг
        CONFIG
        use_re: false
        match_substring: false
        case_sensitive: false
        is_text_disabled: false
        is_file_disabled: true

        :return: текст в формате markdown
        """
        source: dict[str, any] = self.block.get("source", {})

        result_parts: list[str] = [
            self.html_to_markdown(self.soup).strip(),
            "",
            f"ANSWER: {source['pattern']}",
            "",
            "CONFIG",
            *self.dump_config(source, self.step_data)
        ]
        return "\n".join(result_parts) + "\n"


class EssayDump(BaseExporter):
    """Обработка шагов с открытым ответом (ESSAY)"""

    def set_type(self):
        self.step_type = "ESSAY"

    def format_output(self) -> str:
        source: dict[str, any] = self.block.get("source", {})

        self.soup = self.process_code_blocks(self.soup)

        result_parts: list[str] = [
            self.html_to_markdown(self.soup).strip(),
            "",
            "CONFIG",
            *self.dump_config(source, self.step_data)
        ]
        return "\n".join(result_parts) + "\n"


class SortDump(BaseNotImplementedExporter):
    """Заглушка для SORT шагов"""
    pass

class TableDump(BaseExporter):
    """Обработка TABLE шагов (табличные задачи)"""

    def set_type(self):
        self.step_type = "TABLE"

    def _calculate_column_widths(self, rows: list[list[str]]) -> list[int]:
        """Вычисляет максимальную ширину каждой колонки для выравнивания."""
        if not rows:
            return []

        num_cols = len(rows[0])
        widths = [0] * num_cols

        for row in rows:
            for i, cell in enumerate(row):
                cell_len = len(cell)
                if cell_len > widths[i]:
                    widths[i] = cell_len

        return widths

    def _format_table_row(self, row: list[str], widths: list[int]) -> str:
        """Форматирует строку таблицы с выравниванием пробелами."""
        formatted_cells = []
        for i, cell in enumerate(row):
            formatted_cells.append(cell.ljust(widths[i]))
        return "| " + " | ".join(formatted_cells) + " |"

    def _format_separator_row(self, widths: list[int]) -> str:
        """Форматирует строку-разделитель (---) для таблицы."""
        separators = []
        for width in widths:
            separators.append("-" * max(0, width))
        return "| " + " | ".join(separators) + " |"

    def dump_config(self, source: dict, step_data: dict) -> List[str]:
        """Дополняем родительский метод специфичными для TABLE параметрами."""
        config_lines = super().dump_config(source, step_data)

        options = source.get("options", {})

        is_randomize_rows = options.get("is_randomize_rows", True)
        config_lines.append(f"shuffle_rows: {is_randomize_rows}")

        is_randomize_columns = options.get("is_randomize_columns", True)
        config_lines.append(f"shuffle_columns: {is_randomize_columns}")

        is_always_correct = source.get("is_always_correct", False)
        config_lines.append(f"accept_any_answer: {is_always_correct}")

        is_checkbox = options.get("is_checkbox", False)
        config_lines.append(f"allow_multiple: {is_checkbox}")

        return config_lines

    def format_output(self) -> str:
        """Преобразует json в markdown"""
        source: dict[str, any] = self.block.get("source", {})
        options: dict[str, any] = source.get("options", {})

        description = source.get("description", "")
        desc_text = self.html_to_markdown(
            BeautifulSoup(description, "html.parser"),
            has_codeblock=False,
            has_latex=True,
        ).strip()

        columns = source.get("columns", [])
        column_names = []
        for col in columns:
            col_name = col.get("name", "")
            col_text = self.html_to_markdown(BeautifulSoup(col_name, "html.parser")).strip()
            column_names.append(col_text)

        header_row = [desc_text] + column_names

        rows = source.get("rows", [])
        data_rows = []

        for row in rows:
            row_name = row.get("name", "")
            row_text = self.html_to_markdown(BeautifulSoup(row_name, "html.parser")).strip()

            columns_data = row.get("columns", [])
            row_cells = [row_text]

            for col_data in columns_data:
                is_correct = col_data.get("choice", False)
                row_cells.append("+" if is_correct else "")

            data_rows.append(row_cells)

        all_rows = [header_row] + data_rows
        widths = self._calculate_column_widths(all_rows)

        formatted_rows = []
        formatted_rows.append(self._format_table_row(header_row, widths))
        formatted_rows.append(self._format_separator_row(widths))

        for row in data_rows:
            formatted_rows.append(self._format_table_row(row, widths))

        condition_text = self.html_to_markdown(self.soup, has_codeblock=False, has_latex=True).strip()
        config_lines = self.dump_config(source, self.step_data)

        result_parts = [condition_text]
        if condition_text:
            result_parts.append("")

        result_parts.extend(["TABLE", *formatted_rows, "", "CONFIG", *config_lines])

        return "\n".join(result_parts) + "\n"


class CodeDump(BaseNotImplementedExporter):
    """Заглушка для TASKINLINE шагов"""
    pass


class VideoDump(BaseNotImplementedExporter):
    """Заглушка для VIDEO шагов"""
    pass


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

def lesson_snapshot_to_markdown(snapshot: dict) -> str:
    """Преобразует снапшот с json или результат запроса содержимого урока в markdown."""
    lesson_id = snapshot['metadata']['lesson_id']
    lesson_title = snapshot['metadata']['title']
    all_markdown: list[str] = generate_lesson_header(lesson_title, lesson_id)
    # print(f"{all_markdown=}")

    for snapshot_step in snapshot['steps']:
        # print("+++++++++++++++++++++++++++++++++++++++ SNAPSHOT")
        # print(snapshot_step)
        # print("+++++++++++++++++++++++++++++++++++++++ MARKDOWN")
        exporter = get_exporter(step_data=snapshot_step['data']['stepSource'], position=snapshot_step['position'])
        step_markdown = exporter.export()
        # print(step_markdown)
        # print("+++++++++++++++++++++++++++++++++++++++")
        all_markdown.append(step_markdown)

    return '\n'.join(all_markdown)

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

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
HELP_EPILOG = '''\b
Примеры:
  python dump.py 1945916                    Скачать урок с ID 1945916 в lesson_1945916.md
  python dump.py 1945916 -o lesson.md       Скачать урок в указанный файл

\b
Об ошибках сообщайте по адресу: <https://github.com/tatyderb/stepik_deploy/issues>
Репозиторий проекта: <https://github.com/tatyderb/stepik_deploy>
'''


@click.command(context_settings=CONTEXT_SETTINGS, epilog=HELP_EPILOG, no_args_is_help=True)
@click.argument('lesson_id', type=int, required=True, metavar='LESSON_ID')
@click.option('-o', '--output', type=click.Path(), default=None, metavar='FILENAME',
              help='Имя выходного файла (по умолчанию: lesson_{LESSON_ID}.md)')
@click.help_option('-h', '--help', help='Показать эту справку и выйти')
def main(lesson_id: int, output: str | None):
    """
    Скачивание урока со Stepik в markdown файл.
    
    LESSON_ID - ID урока на Stepik (целое число)
    """
    dump_lesson(lesson_id, output)


if __name__ == "__main__":
    main()
