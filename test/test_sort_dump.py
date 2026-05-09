"""
Тесты для дампа SORT шагов (задачи на сортировку/упорядочивание)
"""

from unittest.mock import patch, MagicMock
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.export.dump import SortDump, get_exporter
from src.settings import settings


# ========== ТЕСТ 1: БАЗОВОЕ ФОРМАТИРОВАНИЕ SORT ШАГА ==========


@pytest.fixture
def sort_exporter():
    """Фикстура для создания экземпляра SortDump"""
    step_data = {
        "block": {
            "name": "sorting",
            "text": "<h2>Времена года</h2><p>Расставьте времена года по порядку, начиная с зимы.</p>",
            "source": {
                "options": [
                    {"text": "Зима"},
                    {"text": "Весна"},
                    {"text": "Лето"},
                    {"text": "Осень"},
                ],
                "html": True,
            },
        },
        "cost": 2,
    }
    return SortDump(step_data, 1)


def test_sort_dump_basic_formatting(sort_exporter):
    """Проверка базового форматирования задачи на сортировку"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    result = sort_exporter.export()

    expected = """12345678!@# SORT

## Времена года

Расставьте времена года по порядку, начиная с зимы.

SORT
Зима
====
Весна
====
Лето
====
Осень
====

CONFIG
score: 2
html: True"""

    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


def test_sort_dump_without_title():
    """Проверка экспорта шага без заголовка"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "sorting",
            "text": "<p>Отсортируйте числа по возрастанию.</p>",
            "source": {
                "options": [
                    {"text": "-3"},
                    {"text": "0"},
                    {"text": "2"},
                    {"text": "12"},
                    {"text": "27"},
                    {"text": "100"},
                ],
                "html": False,
            },
        },
        "cost": 1,
    }
    exporter = SortDump(step_data, 5)

    expected = """12345678!@# SORT

Отсортируйте числа по возрастанию.

SORT
-3
====
0
====
2
====
12
====
27
====
100
====

CONFIG
score: 1
html: False"""

    settings.STEP_BEGIN = original
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 2: ПАРАМЕТР HTML ==========


@pytest.mark.parametrize(
    "html_enabled, expected_html",
    [
        (True, "html: True"),
        (False, "html: False"),
    ],
)
def test_sort_dump_html_parameter(html_enabled, expected_html):
    """Проверка параметра html"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "sorting",
            "text": "<h2>Тест с HTML</h2>",
            "source": {
                "options": [{"text": "Первый"}, {"text": "Второй"}],
                "html": html_enabled,
            },
        },
        "cost": 1,
    }
    exporter = SortDump(step_data, 1)

    result = exporter.export()

    assert expected_html in result
    settings.STEP_BEGIN = original


def test_sort_dump_html_in_options():
    """Проверка, что HTML в опциях сохраняется"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "sorting",
            "text": "<h2>Расположите группы по размеру</h2>",
            "source": {
                "options": [
                    {"text": "<ul><li>Холм</li><li>Овраг</li><li>Утес</li></ul>"},
                    {"text": "<ul><li>Горный хребет</li><li>Плато</li></ul>"},
                    {"text": "<ul><li>Материк</li><li>Океан</li></ul>"},
                ],
                "html": True,
            },
        },
        "cost": 1,
    }
    exporter = SortDump(step_data, 1)

    result = exporter.export()

    assert "<ul><li>Холм</li><li>Овраг</li><li>Утес</li></ul>" in result
    assert "<ul><li>Горный хребет</li><li>Плато</li></ul>" in result
    assert "<ul><li>Материк</li><li>Океан</li></ul>" in result
    settings.STEP_BEGIN = original



# ========== ТЕСТ 3: МНОГО ОПЦИЙ ==========


def test_sort_dump_many_options():
    """Проверка большого количества опций"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    options = [{"text": f"Элемент {i+1}"} for i in range(15)]

    step_data = {
        "block": {
            "name": "sorting",
            "text": "<h2>Сортировка 15 элементов</h2>",
            "source": {"options": options, "html": False},
        },
        "cost": 3,
    }
    exporter = SortDump(step_data, 1)

    result = exporter.export()

    for i in range(15):
        assert f"Элемент {i+1}" in result
    settings.STEP_BEGIN = original



# ========== ТЕСТ 4: РЕАЛЬНЫЕ ДАННЫЕ ИЗ STEPIK ==========


def test_sort_dump_real_stepik_data():
    """Проверка форматирования на основе реальных данных из Stepik"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    real_step_data = {
        "id": 9485455,
        "lesson": 2074851,
        "position": 1,
        "block": {
            "name": "sorting",
            "text": "<h2>Времена года</h2>\n<p>Расставьте времена года по порядку, начиная с зимы.</p>",
            "source": {
                "options": [
                    {"text": "Зима"},
                    {"text": "Весна"},
                    {"text": "Лето"},
                    {"text": "Осень"},
                ],
                "html": True,
            },
        },
        "cost": 2,
    }

    exporter = SortDump(real_step_data, 1)

    expected = """12345678!@# SORT

## Времена года

Расставьте времена года по порядку, начиная с зимы.

SORT
Зима
====
Весна
====
Лето
====
Осень
====

CONFIG
score: 2
html: True"""

    settings.STEP_BEGIN = original
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 5: ОДИНОЧНЫЙ ЭЛЕМЕНТ ==========


def test_sort_dump_single_option():
    """Проверка с одним элементом (тривиальная сортировка)"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "sorting",
            "text": "<h2>Один элемент</h2>",
            "source": {
                "options": [{"text": "Единственный элемент"}],
                "html": False,
            },
        },
        "cost": 1,
    }
    exporter = SortDump(step_data, 1)

    expected = """12345678!@# SORT

## Один элемент

SORT
Единственный элемент
====

CONFIG
score: 1
html: False"""

    settings.STEP_BEGIN = original
    assert exporter.export().strip() == expected.strip()

if __name__ == "__main__":
    """Запуск тестов напрямую"""
    import sys

    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    sys.exit(exit_code)
