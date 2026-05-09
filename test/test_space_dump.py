"""
Тесты для экспорта SPACE шагов (заполнение пропусков)
"""
import pytest

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
from src.export.dump import SpaceDump, get_exporter
pytestmark = pytest.mark.step_begin("---1234")


class TestSpaceDump:
    """Тесты для SPACE шагов"""

    @pytest.fixture
    def basic_select_data(self):
        """Шаг с выпадающим списком"""
        return {
            "block": {
                "name": "fill-blanks",
                "text": "<h2>Выберите автора</h2>",
                "source": {
                    "components": [
                        {"type": "text", "text": "Поэму \"Кому на Руси жить хорошо\" написал ", "options": []},
                        {
                            "type": "select",
                            "text": "",
                            "options": [
                                {"text": "Пушкин", "is_correct": False},
                                {"text": "Тургенев", "is_correct": False},
                                {"text": "Некрасов", "is_correct": True}
                            ]
                        }
                    ],
                    "is_case_sensitive": False,
                    "is_detailed_feedback": False,
                    "is_partially_correct": False
                }
            },
            "cost": 2
        }

    @pytest.fixture
    def basic_input_data(self):
        """Шаг с текстовым вводом"""
        return {
            "block": {
                "name": "fill-blanks",
                "text": "<h2>Введите автора</h2>",
                "source": {
                    "components": [
                        {"type": "text", "text": "Автор \"Евгения Онегина\" - ", "options": []},
                        {
                            "type": "input",
                            "text": "",
                            "options": [
                                {"text": "Пушкин", "is_correct": True},
                                {"text": "А.С. Пушкин", "is_correct": True}
                            ]
                        }
                    ],
                    "is_case_sensitive": True,
                    "is_detailed_feedback": True,
                    "is_partially_correct": False
                }
            },
            "cost": 3
        }

    @pytest.fixture
    def mixed_components_data(self):
        """Смешанные компоненты"""
        return {
            "block": {
                "name": "fill-blanks",
                "text": "<h2>Программирование</h2>",
                "source": {
                    "components": [
                        {"type": "text", "text": "Тип ", "options": []},
                        {
                            "type": "select",
                            "text": "",
                            "options": [
                                {"text": "void", "is_correct": True},
                                {"text": "int", "is_correct": False}
                            ]
                        },
                        {"type": "text", "text": " main(", "options": []},
                        {
                            "type": "select",
                            "text": "",
                            "options": [
                                {"text": "void", "is_correct": False},
                                {"text": "int argc", "is_correct": True}
                            ]
                        },
                        {"type": "text", "text": ") { return 0; }", "options": []}
                    ],
                    "is_case_sensitive": False,
                    "is_detailed_feedback": True,
                    "is_partially_correct": True
                }
            },
            "cost": 5
        }

    @pytest.fixture
    def multiple_correct_data(self):
        """Несколько правильных ответов в select"""
        return {
            "block": {
                "name": "fill-blanks",
                "text": "<h2>Столица</h2>",
                "source": {
                    "components": [
                        {"type": "text", "text": "Столица России — ", "options": []},
                        {
                            "type": "select",
                            "text": "",
                            "options": [
                                {"text": "Москва", "is_correct": True},
                                {"text": "Moscow", "is_correct": True},
                                {"text": "Питер", "is_correct": False}
                            ]
                        }
                    ],
                    "is_case_sensitive": True,
                    "is_detailed_feedback": False,
                    "is_partially_correct": False
                }
            },
            "cost": 2
        }

    def test_basic_select(self, basic_select_data):
        exporter = SpaceDump(basic_select_data, position=1)
        result = exporter.export()

        expected = """---1234 SPACE

## Выберите автора

Поэму "Кому на Руси жить хорошо" написал <*[Пушкин], *[Тургенев], [Некрасов]>

CONFIG
score: 2
case_sensitive: False
visual_feedback: False
partial_correct: False

"""

        assert result == expected

    def test_basic_input(self, basic_input_data):
        exporter = SpaceDump(basic_input_data, position=2)
        result = exporter.export()

        expected = """---1234 SPACE

## Введите автора

Автор "Евгения Онегина" - <[Пушкин], [А.С. Пушкин]>

CONFIG
score: 3
case_sensitive: True
visual_feedback: True
partial_correct: False

"""

        assert result == expected

    def test_mixed_components(self, mixed_components_data):
        exporter = SpaceDump(mixed_components_data, position=3)
        result = exporter.export()

        expected = """---1234 SPACE

## Программирование

Тип <[void], *[int]> main(<*[void], [int argc]>) { return 0; }

CONFIG
score: 5
case_sensitive: False
visual_feedback: True
partial_correct: True

"""

        assert result == expected

    def test_multiple_correct(self, multiple_correct_data):
        exporter = SpaceDump(multiple_correct_data, position=4)
        result = exporter.export()

        expected = """---1234 SPACE

## Столица

Столица России — <[Москва], [Moscow], *[Питер]>

CONFIG
score: 2
case_sensitive: True
visual_feedback: False
partial_correct: False

"""

        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])