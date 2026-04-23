from src.settings import settings
import sys
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional, Dict, Any, List, Type
from markdownify import markdownify as md
from bs4 import BeautifulSoup, NavigableString, Tag

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


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
            'choice': ['shuffle'],
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

    @classmethod
    def get_exporter(self, step_data: Dict[str, Any], position: int):
        """Возвращает подходящий экспортер для шага"""
        from src.step_quiz import QuizDump
        from src.step_number import NumberDump
        from src.step_gennumber import GennumberDump
        from src.step_string import StringDump
        from src.step_essay import EssayDump
        from src.step_sort import SortDump
        from src.step_table import TableDump
        from src.step_tasklinline import CodeDump
        from src.step_space import SpaceDump

        block = step_data.get("block", {})
        step_type = block.get("name", "unknown")

        exporters: Dict[str, Type[BaseExporter]] = {
            "text": TextDump,
            "choice": QuizDump,
            "number": NumberDump,
            "random-tasks": GennumberDump,
            "string": StringDump,
            "free-answer": EssayDump,
            "sorting": SortDump,
            "table": TableDump,
            "code": CodeDump,
            "video": VideoDump,
            "fill-blanks": SpaceDump
        }

        exporter_class = exporters.get(step_type, TextDump)
        return exporter_class(step_data, position)


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


class VideoDump(BaseNotImplementedExporter):
    """Заглушка для VIDEO шагов"""
    pass


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Использование: python dump.py LESSON_ID [filename]")
    #     sys.exit(1)
    #
    # lesson_id = int(sys.argv[1])
    # filename = sys.argv[2] if len(sys.argv) > 2 else None
    #
    # dump_lesson(lesson_id, filename)
    t = TextDump({'block': {'text': '', 'name': 'text'}}, 1)
    print(t.export())
