import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


import pytest
from bs4 import BeautifulSoup
from src.export.text_dump import TextDump, BaseExporter


class TestHeaderReduction:
    """Тесты для проверки понижения заголовков с добавлением REDUCE-N"""

    @pytest.fixture
    def exporter(self):
        """Фикстура для создания базового экспортера"""
        step_data = {"block": {"text": "", "name": "text"}}
        return BaseExporter(step_data, 1)

    @pytest.fixture
    def text_exporter(self):
        """Фикстура для создания TextDump экспортера"""
        step_data = {"block": {"text": "", "name": "text"}}
        return TextDump(step_data, 1)

    def test_single_header_reduction(self, exporter):
        """Тест понижения одного заголовка"""
        markdown = "# Header 1\nSome text"
        expected = "### REDUCE-2 Header 1\nSome text"

        result = exporter.adjust_header_levels(markdown, base_level=3)
        assert result == expected

    def test_multiple_headers_reduction(self, exporter):
        """Тест понижения нескольких заголовков разного уровня"""
        markdown = """# Header 1
text
## Header 2
text
### Header 2.1
#### Header 2.1.1"""

        expected = """### REDUCE-2 Header 1
text
#### REDUCE-2 Header 2
text
##### REDUCE-2 Header 2.1
###### REDUCE-2 Header 2.1.1"""

        result = exporter.adjust_header_levels(markdown, base_level=3)
        assert result == expected

    def test_different_reduction_levels(self, exporter):
        """Тест разных уровней понижения"""
        markdown = "# Header 1\n## Header 2"

        # Понижение на 1 уровень (base_level=2)
        expected_1 = "## REDUCE-1 Header 1\n### REDUCE-1 Header 2"
        result_1 = exporter.adjust_header_levels(markdown, base_level=2)
        assert result_1 == expected_1

        # Понижение на 2 уровня (base_level=3)
        expected_2 = "### REDUCE-2 Header 1\n#### REDUCE-2 Header 2"
        result_2 = exporter.adjust_header_levels(markdown, base_level=3)
        assert result_2 == expected_2

        # Понижение на 3 уровня (base_level=4)
        expected_3 = "#### REDUCE-3 Header 1\n##### REDUCE-3 Header 2"
        result_3 = exporter.adjust_header_levels(markdown, base_level=4)
        assert result_3 == expected_3


    def test_mixed_content_with_headers(self, exporter):
        """Тест смешанного контента (заголовки + обычный текст)"""
        markdown = """# Главный заголовок
Обычный текст с *форматированием*

## Подзаголовок
- список
- элементов

### Заголовок 3 уровня
Код: `print("hello")`"""

        expected = """### REDUCE-2 Главный заголовок
Обычный текст с *форматированием*

#### REDUCE-2 Подзаголовок
- список
- элементов

##### REDUCE-2 Заголовок 3 уровня
Код: `print("hello")`"""

        result = exporter.adjust_header_levels(markdown, base_level=3)
        assert result == expected


    def test_max_header_level(self, exporter):
        """Тест максимального уровня заголовков (не больше 6)"""
        markdown = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"

        # Понижение на 3 уровня (должны остановиться на ######)
        expected = "#### REDUCE-3 H1\n##### REDUCE-3 H2\n###### REDUCE-3 H3\n###### REDUCE-3 H4\n###### REDUCE-3 H5\n###### REDUCE-3 H6"

        result = exporter.adjust_header_levels(markdown, base_level=4)
        assert result == expected

    def test_real_example_from_description(self, text_exporter, monkeypatch):
        """Тест на примере из описания задачи"""
        html = """
        <h1>Header 1</h1>
        <p>text</p>
        <h1>Header 2</h1>
        <p>text</p>
        <h2>Header 2.1</h2>
        <h3>Header 2.1.1</h3>
        """

        text_exporter.soup = BeautifulSoup(html, "html.parser")
        text_exporter.html = html

        def mock_md(*args, **kwargs):
            return """# Header 1
text
# Header 2
text
## Header 2.1
### Header 2.1.1"""

        monkeypatch.setattr("src.export.text_dump.md", mock_md)

        result = text_exporter.format_output("TEXT")

        expected = """## TEXT

### REDUCE-2 Header 1
text
### REDUCE-2 Header 2
text
#### REDUCE-2 Header 2.1
##### REDUCE-2 Header 2.1.1"""

        assert result.strip() == expected.strip()
