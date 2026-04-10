"""
Тесты для дампа MATCH шагов (задачи на сопоставление)
"""

from unittest.mock import patch, MagicMock
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.export.dump import MatchDump, get_exporter
from src.settings import settings


# ========== ТЕСТ 1: БАЗОВОЕ ФОРМАТИРОВАНИЕ MATCH ШАГА ==========


@pytest.fixture
def match_exporter():
    """Фикстура для создания экземпляра MatchDump"""
    step_data = {
        "block": {
            "name": "matching",
            "text": "<h2>Авторы и произведения</h2><p>Кто автор произведения?</p>",
            "source": {
                "pairs": [
                    {"first": "Муму", "second": "Тургенев И.С."},
                    {"first": "Война и мир", "second": "Толстой Л.Н."},
                    {"first": "Бородино", "second": "Лермонтов М.Ю."},
                ],
                "preserve_firsts_order": True,
                "html": True,
            },
        },
        "cost": 1,
    }
    return MatchDump(step_data, 1)


def test_match_dump_basic_formatting(match_exporter):
    """Проверка базового форматирования задачи на сопоставление"""
    result = match_exporter.export()

    # Проверяем наличие ключевых элементов
    assert "MATCH" in result
    assert "Муму" in result
    assert "Тургенев И.С." in result
    assert "Война и мир" in result
    assert "Толстой Л.Н." in result
    assert "Бородино" in result
    assert "Лермонтов М.Ю." in result
    assert "CONFIG" in result
    assert "shuffle: False" in result
    assert "score: 1" in result
    assert "html: True" in result
    assert "## Авторы и произведения" in result
    assert "Кто автор произведения?" in result


def test_match_dump_without_title():
    """Проверка экспорта шага без заголовка"""
    step_data = {
        "block": {
            "name": "matching",
            "text": "<p>Сопоставьте страну и столицу.</p>",
            "source": {
                "pairs": [
                    {"first": "Россия", "second": "Москва"},
                    {"first": "Франция", "second": "Париж"},
                    {"first": "Германия", "second": "Берлин"},
                ],
                "preserve_firsts_order": True,
                "html": False,
            },
        },
        "cost": 2,
    }
    exporter = MatchDump(step_data, 5)
    result = exporter.export()

    # Проверяем ключевые элементы
    assert "MATCH" in result
    assert "Сопоставьте страну и столицу" in result
    assert "Россия" in result
    assert "Москва" in result
    assert "Франция" in result
    assert "Париж" in result
    assert "Германия" in result
    assert "Берлин" in result
    assert "shuffle: False" in result
    assert "score: 2" in result
    assert "html: False" in result


# ========== ТЕСТ 2: ПАРАМЕТР SHUFFLE ==========


@pytest.mark.parametrize(
    "preserve_order, expected_shuffle",
    [
        (True, "shuffle: False"),
        (False, "shuffle: True"),
    ],
)
def test_match_dump_shuffle_parameter(preserve_order, expected_shuffle):
    """Проверка параметра shuffle (preserve_firsts_order)"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "matching",
            "text": "<h2>Тест с перемешиванием</h2>",
            "source": {
                "pairs": [{"first": "A", "second": "1"}, {"first": "B", "second": "2"}],
                "preserve_firsts_order": preserve_order,
                "html": True,
            },
        },
        "cost": 1,
    }
    exporter = MatchDump(step_data, 1)

    result = exporter.export()

    assert expected_shuffle in result
    settings.STEP_BEGIN = original


# ========== ТЕСТ 3: HTML ТЕГИ В ПАРАХ ==========


def test_match_dump_html_in_pairs():
    """Проверка, что HTML в парах сохраняется"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    step_data = {
        "block": {
            "name": "matching",
            "text": "<h2>Сопоставьте флаги</h2>",
            "source": {
                "pairs": [
                    {"first": "Россия", "second": '<img src="flag_ru.png">'},
                    {"first": "Франция", "second": '<img src="flag_fr.png">'},
                ],
                "preserve_firsts_order": True,
                "is_html_enabled": True,
            },
        },
        "cost": 1,
    }
    exporter = MatchDump(step_data, 1)

    result = exporter.export()

    assert '<img src="flag_ru.png">' in result
    assert '<img src="flag_fr.png">' in result
    settings.STEP_BEGIN = original



# ========== ТЕСТ 4: МНОГО ПАР ==========


def test_match_dump_many_pairs():
    """Проверка большого количества пар"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    pairs = []
    for i in range(10):
        pairs.append({"first": f"Термин {i+1}", "second": f"Определение {i+1}"})

    step_data = {
        "block": {
            "name": "matching",
            "text": "<h2>Большое сопоставление</h2>",
            "source": {
                "pairs": pairs,
                "preserve_firsts_order": True,
                "is_html_enabled": False,
            },
        },
        "cost": 5,
    }
    exporter = MatchDump(step_data, 1)

    result = exporter.export()

    for i in range(10):
        assert f"Термин {i+1}" in result
        assert f"Определение {i+1}" in result
    settings.STEP_BEGIN = original



# ========== ТЕСТ 5: РЕАЛЬНЫЕ ДАННЫЕ ИЗ STEPIK ==========


def test_match_dump_real_stepik_data():
    """Проверка форматирования на основе реальных данных из Stepik"""
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345678!@#"

    real_step_data = {
        "id": 9485454,
        "lesson": 2237157,
        "position": 1,
        "block": {
            "name": "matching",
            "text": "<h2>Авторы и произведения</h2>\n<p>Кто автор произведения?</p>",
            "source": {
                "pairs": [
                    {"first": "Муму", "second": "Тургенев И.С."},
                    {"first": "Война и мир", "second": "Толстой Л.Н."},
                    {"first": "Бородино", "second": "Лермонтов М.Ю."},
                ],
                "preserve_firsts_order": True,
                "html": True,
            },
        },
        "cost": 2,
    }

    exporter = MatchDump(real_step_data, 1)

    expected = """12345678!@# MATCH

## Авторы и произведения

Кто автор произведения?

MATCH
Муму
----
Тургенев И.С.
====
Война и мир
----
Толстой Л.Н.
====
Бородино
----
Лермонтов М.Ю.
====

CONFIG
shuffle: False
score: 2
html: True"""

    settings.STEP_BEGIN = original
    assert exporter.export().strip() == expected.strip()


if __name__ == "__main__":
    """Запуск тестов напрямую"""
    import sys

    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    sys.exit(exit_code)
