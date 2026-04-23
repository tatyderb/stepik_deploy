"""Тесты для экспорта ESSAY шагов"""

import pytest
from dump import EssayDump, get_exporter


pytestmark = pytest.mark.step_begin("---1234")

@pytest.fixture
def basic_essay_data():
    """Фикстура: простой ESSAY шаг"""
    return {
        "block": {
            "name": "free-answer",
            "text": "<h2>Ваше мнение</h2><p>Опишите преимущества Python.</p>",
            "source": {
                "is_attachments_enabled": False,
                "is_html_enabled": True,
                "manual_scoring": False,
            },
        },
        "cost": 2,
    }


@pytest.fixture
def essay_without_title():
    """Фикстура: ESSAY шаг без заголовка"""
    return {
        "block": {
            "name": "free-answer",
            "text": "<p>Какой язык программирования вы предпочитаете?</p>",
            "source": {
                "is_attachments_enabled": True,
                "is_html_enabled": False,
                "manual_scoring": True,
            },
        },
        "cost": 5,
    }


def test_essay_basic_export(basic_essay_data):
    """Проверка базового экспорта ESSAY шага"""
    exporter = EssayDump(basic_essay_data, position=1)
    result = exporter.export()

    expected = """---1234 ESSAY

## Ваше мнение

Опишите преимущества Python.

CONFIG
score: 2
is_attachments_enabled: False
is_html_enabled: True
manual_scoring: False"""

    assert result.strip() == expected.strip()


def test_essay_without_title(essay_without_title):
    """Проверка экспорта ESSAY шага без заголовка"""
    exporter = EssayDump(essay_without_title, position=3)
    result = exporter.export()

    expected = """---1234 ESSAY

Какой язык программирования вы предпочитаете?

CONFIG
score: 5
is_attachments_enabled: True
is_html_enabled: False
manual_scoring: True"""

    assert result.strip() == expected.strip()


def test_essay_with_latex():
    """Проверка конвертации LaTeX в ESSAY шаге"""
    step_data = {
        "block": {
            "name": "free-answer",
            "text": "<h2>Формула</h2><p>Объясните смысл \\(E=mc^2\\).</p>",
            "source": {
                "is_attachments_enabled": False,
                "is_html_enabled": True,
                "manual_scoring": False,
            },
        },
        "cost": 1,
    }
    exporter = EssayDump(step_data, position=1)
    result = exporter.export()

    expected = """---1234 ESSAY

## Формула

Объясните смысл $E=mc^2$.

CONFIG
score: 1
is_attachments_enabled: False
is_html_enabled: True
manual_scoring: False"""

    assert result.strip() == expected.strip()


def test_get_exporter_returns_essay_dump():
    """Проверка, что get_exporter возвращает EssayDump для free-answer шагов"""
    step_data = {"block": {"name": "free-answer", "text": "<p>Тест</p>"}}
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, EssayDump)


def test_essay_all_config_options():
    """Проверка экспорта ESSAY шага со всеми возможными опциями конфигурации"""
    step_data = {
        "block": {
            "name": "free-answer",
            "text": "<h2>Полный набор опций</h2><p>Тестирование всех настроек</p>",
            "source": {
                "is_attachments_enabled": True,
                "is_html_enabled": True,
                "manual_scoring": True,
            },
        },
        "cost": 10,
    }
    exporter = EssayDump(step_data, position=2)
    result = exporter.export()

    expected = """---1234 ESSAY

## Полный набор опций

Тестирование всех настроек

CONFIG
score: 10
is_attachments_enabled: True
is_html_enabled: True
manual_scoring: True"""

    assert result.strip() == expected.strip()


def test_essay_minimal_config():
    """Проверка экспорта ESSAY шага с минимальными настройками"""
    step_data = {
        "block": {
            "name": "free-answer",
            "text": "<h2>Минимальные настройки</h2><p>Только текст</p>",
            "source": {
                "is_attachments_enabled": False,
                "is_html_enabled": False,
                "manual_scoring": True,
            },
        },
        "cost": 1,
    }
    exporter = EssayDump(step_data, position=1)
    result = exporter.export()

    expected = """---1234 ESSAY

## Минимальные настройки

Только текст

CONFIG
score: 1
is_attachments_enabled: False
is_html_enabled: False
manual_scoring: True"""

    assert result.strip() == expected.strip()
