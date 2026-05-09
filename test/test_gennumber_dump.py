"""
Тесты для дампа GENNUMBER шагов (численная задача со случайной генерацией условия)
"""

import pytest

from src.export.dump import GennumberDump


pytestmark = pytest.mark.step_begin("---1234")


# ========== ТЕСТ 1: БАЗОВОЕ ФОРМАТИРОВАНИЕ ==========

def test_gennumber_basic():
    """Простая задача с двумя переменными, без погрешности"""
    step_data = {
        'block': {
            'name': 'random-tasks',
            'text': '',
            'source': {
                'task': 'В саду цветут яблони и груши.\nПчела опылила \\x цветочков, а шмель \\y.\nСколько цветочков они опылили вместе?',
                'solve': 'x+y',
                'max_error': '0',
                'ranges': [
                    {'variable': 'x', 'num_from': '1', 'num_to': '20', 'num_step': '1'},
                    {'variable': 'y', 'num_from': '1', 'num_to': '15', 'num_step': '1'}
                ]
            }
        },
        'cost': 2
    }
    exporter = GennumberDump(step_data, 1)

    expected = r"""---1234 GENNUMBER



CONDITION

В саду цветут яблони и груши.
Пчела опылила \x цветочков, а шмель \y.
Сколько цветочков они опылили вместе?

ANSWER
x+y

VAR
x (1, 20, 1)
y (1, 15, 1)

CONFIG
score: 2"""

    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 2: ЗАДАЧА С ПОГРЕШНОСТЬЮ ==========

def test_gennumber_with_tolerance():
    """Задача с погрешностью - должна появиться конструкция '+-'"""
    step_data = {
        'block': {
            'name': 'random-tasks',
            'text': '',
            'source': {
                'task': 'Пчела облетела яблоню по траектории с радиусом \\r м\nКакой путь пролетела пчела в сантиметрах?',
                'solve': '2 * 3.14 * 100 * r',
                'max_error': '2.0',
                'ranges': [
                    {'variable': 'r', 'num_from': '0.2', 'num_to': '2', 'num_step': '0.1'}
                ]
            }
        },
        'cost': 1
    }
    exporter = GennumberDump(step_data, 1)

    expected = r"""---1234 GENNUMBER



CONDITION

Пчела облетела яблоню по траектории с радиусом \r м
Какой путь пролетела пчела в сантиметрах?

ANSWER
2 * 3.14 * 100 * r +- 2.0

VAR
r (0.2, 2, 0.1)

CONFIG
score: 1"""

    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 3: ЗАДАЧА С ТРЕМЯ ПЕРЕМЕННЫМИ ==========

def test_gennumber_three_variables():
    """Три переменные с разными диапазонами"""
    step_data = {
        'block': {
            'name': 'random-tasks',
            'text': '',
            'source': {
                'task': 'Мельница, работая по \\h часов в день, намолола за 6 дней \\a ц муки. Сколько часов должна работать мельница, чтобы за 8 дней намолоть \\b т муки?',
                'solve': '(6 * b * 10) / (8 * a) * h',
                'max_error': '0',
                'ranges': [
                    {'variable': 'h', 'num_from': '1', 'num_to': '24', 'num_step': '1'},
                    {'variable': 'a', 'num_from': '100', 'num_to': '300', 'num_step': '100'},
                    {'variable': 'b', 'num_from': '0', 'num_to': '100', 'num_step': '1'}
                ]
            }
        },
        'cost': 3
    }
    exporter = GennumberDump(step_data, 1)

    expected = r"""---1234 GENNUMBER



CONDITION

Мельница, работая по \h часов в день, намолола за 6 дней \a ц муки. Сколько часов должна работать мельница, чтобы за 8 дней намолоть \b т муки?

ANSWER
(6 * b * 10) / (8 * a) * h

VAR
h (1, 24, 1)
a (100, 300, 100)
b (0, 100, 1)

CONFIG
score: 3"""

    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 4: ЗАДАЧА БЕЗ ПЕРЕМЕННЫХ ==========

def test_gennumber_no_variables():
    """Задача без переменных (только константа)"""
    step_data = {
        'block': {
            'name': 'random-tasks',
            'text': '',
            'source': {
                'task': 'Сколько будет 2 + 2?',
                'solve': '4',
                'max_error': '0',
                'ranges': []
            }
        },
        'cost': 1
    }
    exporter = GennumberDump(step_data, 1)

    expected = r"""---1234 GENNUMBER



CONDITION

Сколько будет 2 + 2?

ANSWER
4

VAR

CONFIG
score: 1"""

    assert exporter.export().strip() == expected.strip()
