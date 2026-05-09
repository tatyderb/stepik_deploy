"""
Тесты для экспорта TABLE шагов (табличные задачи)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest

from src.export.dump import TableDump, get_exporter

pytestmark = pytest.mark.step_begin("---1234")

@pytest.fixture
def basic_table_data():
    """Фикстура: базовая таблица"""
    return {
        "block": {
            "name": "table",
            "text": "<h2>Таблица истинности</h2><p>Выберете истинное выражение.</p>",
            "source": {
                "description": "Ряды:",
                "columns": [
                    {"name": "A=0,B=0"},
                    {"name": "A=0,B=1"},
                    {"name": "A=1,B=0"},
                    {"name": "A=1,B=1"},
                ],
                "rows": [
                    {
                        "name": "A AND B",
                        "columns": [
                            {"choice": False},
                            {"choice": False},
                            {"choice": False},
                            {"choice": True},
                        ],
                    }
                ],
                "options": {
                    "is_randomize_rows": True, 
                    "is_randomize_columns": True},
                "is_always_correct": False,
            },
        },
        "cost": 2,
    }


@pytest.fixture
def allow_multiple_table_data():
    """Фикстура: таблица с множественным выбором"""
    return {
        "block": {
            "name": "table",
            "text": "<h2>Выбор характеристик</h2>",
            "source": {
                "description": "Объекты:",
                "columns": [
                    {"name": "Прозрачный"},
                    {"name": "Газообразный"},
                    {"name": "Жидкий"},
                ],
                "rows": [
                    {
                        "name": "Вода",
                        "columns": [
                            {"choice": True},
                            {"choice": False},
                            {"choice": True},
                        ],
                    }
                ],
                "options": {
                    "is_randomize_rows": True,
                    "is_randomize_columns": True,
                    "is_checkbox": True,
                },
                "is_always_correct": False,
            },
        },
        "cost": 4,
    }


@pytest.fixture
def accept_any_answer_table_data():
    """Фикстура: таблица-опрос (любой ответ верный)"""
    return {
        "block": {
            "name": "table",
            "text": "<h2>Опрос</h2><p>Оцените курс.</p>",
            "source": {
                "description": "Критерии:",
                "columns": [{"name": "1"}, {"name": "2"}, {"name": "3"}],
                "rows": [
                    {
                        "name": "Качество",
                        "columns": [
                            {"choice": False},
                            {"choice": False},
                            {"choice": False},
                        ],
                    }
                ],
                "options": {"is_randomize_rows": False, "is_randomize_columns": False},
                "is_always_correct": True,
            },
        },
        "cost": 0,
    }


@pytest.fixture
def without_config_options_table_data():
    """Фикстура: таблица без указанных опций (значения по умолчанию)"""
    return {
        "block": {
            "name": "table",
            "text": "<p>Простая таблица</p>",
            "source": {
                "description": "Тест:",
                "columns": [{"name": "Колонка 1"}, {"name": "Колонка 2"}],
                "rows": [
                    {
                        "name": "Строка 1",
                        "columns": [{"choice": True}, {"choice": False}],
                    }
                ],
            },
        },
        "cost": 2,
    }


def test_table_dump(basic_table_data):
    """Проверка базовой таблицы"""
    exporter = TableDump(basic_table_data, position=1)
    result = exporter.export()

    expected = """---1234 TABLE

## Таблица истинности

Выберете истинное выражение.

TABLE
| Ряды:   | A=0,B=0 | A=0,B=1 | A=1,B=0 | A=1,B=1 |
| ------- | ------- | ------- | ------- | ------- |
| A AND B |         |         |         | +       |

CONFIG
score: 2
shuffle_rows: True
shuffle_columns: True
accept_any_answer: False
allow_multiple: False

"""

    assert result == expected


def test_table_dump_allow_multiple(allow_multiple_table_data):
    """Проверка таблицы с множественным выбором"""
    exporter = TableDump(allow_multiple_table_data, position=5)
    result = exporter.export()

    expected = """---1234 TABLE

## Выбор характеристик

TABLE
| Объекты: | Прозрачный | Газообразный | Жидкий |
| -------- | ---------- | ------------ | ------ |
| Вода     | +          |              | +      |

CONFIG
score: 4
shuffle_rows: True
shuffle_columns: True
accept_any_answer: False
allow_multiple: True

"""

    assert result == expected


def test_table_dump_accept_any_answer(accept_any_answer_table_data):
    """Проверка таблицы-опроса (любой ответ верный)"""
    exporter = TableDump(accept_any_answer_table_data, position=4)
    result = exporter.export()

    expected = """---1234 TABLE

## Опрос

Оцените курс.

TABLE
| Критерии: | 1 | 2 | 3 |
| --------- | - | - | - |
| Качество  |   |   |   |

CONFIG
score: 0
shuffle_rows: False
shuffle_columns: False
accept_any_answer: True
allow_multiple: False

"""

    assert result == expected


def test_table_dump_without_config_options(without_config_options_table_data):
    """Проверка таблицы без указанных опций (значения по умолчанию)"""
    exporter = TableDump(without_config_options_table_data, position=1)
    result = exporter.export()

    expected = """---1234 TABLE

Простая таблица

TABLE
| Тест:    | Колонка 1 | Колонка 2 |
| -------- | --------- | --------- |
| Строка 1 | +         |           |

CONFIG
score: 2
shuffle_rows: True
shuffle_columns: True
accept_any_answer: False
allow_multiple: False

"""

    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
