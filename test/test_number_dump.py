"""
Тесты для дампа численных задач (NUMBER шагов)
"""

from unittest.mock import patch, MagicMock, call
import pytest
import json
from bs4 import BeautifulSoup

from src.export.dump import NumberDump, get_exporter


# ========== ТЕСТ 1: БАЗОВОЕ ФОРМАТИРОВАНИЕ NUMBER ШАГА ==========

@pytest.fixture
def number_exporter():
    """Фикстура для создания экземпляра NumberDump"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тестовый заголовок</h2><p>Чему равно 2+2?</p>',
            'source': {
                'options': [
                    {'answer': '4', 'max_error': '0'}
                ],
                'sample_size': 1,
                'is_options_feedback': False
            }
        },
        'cost': 2
    }
    return NumberDump(step_data, 1)


def test_number_dump_basic_formatting(number_exporter):
    """Проверка базового форматирования численной задачи"""
    result = number_exporter.export()
    
    expected = """## NUMBER Тестовый заголовок

Чему равно 2+2?

ANSWER: 4

CONFIG
score: 2"""
    
    assert result.strip() == expected.strip()


def test_number_dump_without_title():
    """Проверка экспорта шага без заголовка"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<p>Просто текст без заголовка</p>',
            'source': {
                'options': [
                    {'answer': '42', 'max_error': '0'}
                ]
            }
        },
        'cost': 1
    }
    exporter = NumberDump(step_data, 5)
    
    expected = """## NUMBER Шаг 5

Просто текст без заголовка

ANSWER: 42

CONFIG
score: 1"""
    
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 2: ФОРМАТИРОВАНИЕ С ТОЧНОСТЬЮ ==========

@pytest.mark.parametrize("answer, max_error, expected_answer", [
    ('3.14', '0.01', 'ANSWER: 3.14 +-0.01'),
    ('0.333', '0.001', 'ANSWER: 0.333 +-0.001'),
    ('5', '0', 'ANSWER: 5'),
    ('-7.5', '0.1', 'ANSWER: -7.5 +-0.1'),
    ('100', '0.5', 'ANSWER: 100 +-0.5'),
])
def test_number_dump_with_accuracy(answer, max_error, expected_answer):
    """Проверка форматирования ответов с точностью"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тест с точностью</h2>',
            'source': {
                'options': [
                    {'answer': answer, 'max_error': max_error}
                ]
            }
        },
        'cost': 1
    }
    exporter = NumberDump(step_data, 1)
    
    expected = f"""## NUMBER Тест с точностью

{expected_answer}

CONFIG
score: 1"""
    
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 3: МНОЖЕСТВЕННЫЕ ОТВЕТЫ ==========

def test_number_dump_multiple_answers():
    """Проверка форматирования нескольких ответов"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Найдите корни уравнения x^2-3x+2=0</h2>',
            'source': {
                'options': [
                    {'answer': '1', 'max_error': '0'},
                    {'answer': '2', 'max_error': '0'}
                ],
                'sample_size': 2
            }
        },
        'cost': 3
    }
    exporter = NumberDump(step_data, 1)
    
    expected = """## NUMBER Найдите корни уравнения x^2-3x+2=0

ANSWER: 1
ANSWER: 2

CONFIG
score: 3"""
    
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 4: ПРОВЕРКА БЕЛЫХ СПИСКОВ ==========

def test_number_dump_white_list():
    """Проверка, что только разрешенные параметры попадают в CONFIG (для NUMBER белый список пустой)"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тест с параметрами</h2>',
            'source': {
                'options': [{'answer': '5', 'max_error': '0'}],
                'sample_size': 1,
                'is_options_feedback': False,
                'some_custom_param': 'value'
            }
        },
        'cost': 1
    }
    exporter = NumberDump(step_data, 1)
    
    expected = """## NUMBER Тест с параметрами

ANSWER: 5

CONFIG
score: 1"""
    
    result = exporter.export().strip()
    assert result == expected.strip()
    
    assert "sample_size" not in result
    assert "is_options_feedback" not in result
    assert "some_custom_param" not in result


# ========== ТЕСТ 5: ПРОВЕРКА ИЗВЛЕЧЕНИЯ ЗАГОЛОВКА ==========

def test_number_dump_extract_title():
    """Проверка извлечения заголовка из HTML"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h3>Важный заголовок</h3><p>Текст задачи</p>',
            'source': {
                'options': [{'answer': '7', 'max_error': '0'}]
            }
        },
        'cost': 2
    }
    exporter = NumberDump(step_data, 1)
    
    expected = """## NUMBER Важный заголовок

Текст задачи

ANSWER: 7

CONFIG
score: 2"""
    
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 6: ПРОВЕРКА С ID ШАГАМИ ИЗ РЕАЛЬНЫХ ДАННЫХ ==========

def test_number_dump_with_real_data_format():
    """Проверка форматирования на основе реального урока Stepik 1950069"""
    
    real_step_data = {
        "id": 9775138,
        "lesson": 1950069,
        "position": 5,
        "block": {
            "name": "number",
            "text": "<p>Шаг без заголовка.</p>\n\n<p>Чему равно 2 + 3?</p>",
            "source": {
                "options": [
                    {
                        "answer": "5.0",
                        "max_error": "0"
                    }
                ]
            }
        },
        "cost": 2
    }
    
    exporter = NumberDump(real_step_data, 5)
    
    expected = """## NUMBER Шаг 5

Шаг без заголовка.

Чему равно 2 + 3?

ANSWER: 5.0

CONFIG
score: 2"""
    
    assert exporter.export().strip() == expected.strip()

# ========== ТЕСТ 7: ПРОВЕРКА ФУНКЦИИ GET_EXPORTER ==========

def test_get_exporter_returns_number_dump():
    """Проверка, что get_exporter возвращает NumberDump для number шагов"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<p>Тест</p>'
        }
    }
    
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, NumberDump)


# ========== ТЕСТ 8: ПРОВЕРКА С РАЗНЫМИ ЗНАЧЕНИЯМИ SCORE ==========

@pytest.mark.parametrize("score_value, expected_score", [
    (1, "score: 1"),
    (3, "score: 3"),
    (5, "score: 5"),
    (10, "score: 10"),
    (0, "score: 0"),
])
def test_number_dump_score_values(score_value, expected_score):
    """Проверка разных значений score"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тест с разными баллами</h2>',
            'source': {
                'options': [{'answer': '5', 'max_error': '0'}]
            }
        },
        'cost': score_value
    }
    exporter = NumberDump(step_data, 1)
    
    expected = f"""## NUMBER Тест с разными баллами

ANSWER: 5

CONFIG
{expected_score}"""
    
    assert exporter.export().strip() == expected.strip()


# ========== ТЕСТ 9: ПРОВЕРКА ОБРАБОТКИ НЕКОРРЕКТНОГО MAX_ERROR ==========

def test_number_dump_invalid_max_error(capsys):
    """Проверка обработки некорректного значения max_error"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тест с некорректной погрешностью</h2>',
            'source': {
                'options': [
                    {'answer': '10.5', 'max_error': 'invalid_value'}
                ]
            }
        },
        'cost': 2
    }
    exporter = NumberDump(step_data, position=5)
    result = exporter.export()
    
    captured = capsys.readouterr()
    assert "WARNING: Некорректное значение max_error='invalid_value' для ответа '10.5' в шаге 5" in captured.err
    
    expected = """## NUMBER Тест с некорректной погрешностью

ANSWER: 10.5

CONFIG
score: 2"""
    
    assert result.strip() == expected.strip()


def test_number_dump_invalid_max_error_multiple_answers(capsys):
    """Проверка обработки некорректного max_error среди нескольких ответов"""
    step_data = {
        'block': {
            'name': 'number',
            'text': '<h2>Тест с несколькими ответами и ошибкой в одном</h2>',
            'source': {
                'options': [
                    {'answer': '1.0', 'max_error': '0.0'},
                    {'answer': '2.0', 'max_error': 'invalid'},
                    {'answer': '3.0', 'max_error': '0.5'}
                ]
            }
        },
        'cost': 3
    }
    exporter = NumberDump(step_data, position=10)
    result = exporter.export()
    
    captured = capsys.readouterr()
    assert "WARNING: Некорректное значение max_error='invalid' для ответа '2.0' в шаге 10" in captured.err
    
    expected = """## NUMBER Тест с несколькими ответами и ошибкой в одном

ANSWER: 1.0
ANSWER: 2.0
ANSWER: 3.0 +-0.5

CONFIG
score: 3"""
    
    assert result.strip() == expected.strip()

# ========== ТЕСТ 10: ПОЛНЫЙ УРОК С NUMBER ШАГАМИ ==========

def test_complete_number_lesson():
    """Проверка полного урока с несколькими number шагами"""
    
    mock_step_data = [
        # Шаг 1
        {
            'block': {
                'name': 'number',
                'text': '<h2>Простой вопрос</h2><p>2 + 2 = ?</p>',
                'source': {
                    'options': [{'answer': '4', 'max_error': '0'}]
                }
            },
            'cost': 1
        },
        # Шаг 2
        {
            'block': {
                'name': 'number',
                'text': '<h2>С точностью</h2><p>Чему равно 1/3?</p>',
                'source': {
                    'options': [{'answer': '0.333', 'max_error': '0.001'}]
                }
            },
            'cost': 2
        },
        # Шаг 3
        {
            'block': {
                'name': 'number',
                'text': '<h2>Два корня</h2><p>Найдите корни x^2-5x+6=0</p>',
                'source': {
                    'options': [
                        {'answer': '2', 'max_error': '0'},
                        {'answer': '3', 'max_error': '0'}
                    ]
                }
            },
            'cost': 3
        }
    ]
    
    exporters = [NumberDump(data, i+1) for i, data in enumerate(mock_step_data)]
    
    lesson_parts = [
        "# Численные задачи",
        "",
        "lesson: 12345",
        ""
    ]
    
    for exporter in exporters:
        lesson_parts.append(exporter.export())
    
    expected_lesson = """# Численные задачи

lesson: 12345

## NUMBER Простой вопрос

2 + 2 = ?

ANSWER: 4

CONFIG
score: 1

## NUMBER С точностью

Чему равно 1/3?

ANSWER: 0.333 +-0.001

CONFIG
score: 2

## NUMBER Два корня

Найдите корни x^2-5x+6=0

ANSWER: 2
ANSWER: 3

CONFIG
score: 3"""

    
    result = "\n".join(lesson_parts).strip()
    assert result == expected_lesson