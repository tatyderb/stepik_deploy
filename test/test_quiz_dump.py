"""
Тесты для дампа QUIZ шагов
"""

import pytest
from src.export.dump import QuizDump, get_exporter, settings


@pytest.fixture
def quiz_single():
    """QUIZ с одним правильным ответом"""
    return QuizDump({
        'block': {
            'name': 'choice',
            'text': '<h2>Выбор одного</h2><p>2 + 3 = ?</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p>5</p>'},
                    {'is_correct': False, 'text': '<p>-5</p>'},
                    {'is_correct': False, 'text': '<p>0</p>'},
                    {'is_correct': False, 'text': '<p>55</p>'}
                ],
                'is_multiple_choice': False
            }
        },
        'cost': 1
    }, 1)


@pytest.fixture
def quiz_multiple():
    """QUIZ с несколькими правильными ответами"""
    return QuizDump({
        'block': {
            'name': 'choice',
            'text': '<h2>Выбор нескольких</h2><p>? = 12</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p>6 * 2</p>'},
                    {'is_correct': False, 'text': '<p>7 - 18</p>'},
                    {'is_correct': False, 'text': '<p>1 + 2</p>'},
                    {'is_correct': True, 'text': '<p>9 + 3</p>'}
                ],
                'is_multiple_choice': True
            }
        },
        'cost': 2
    }, 1)


# ========== ТЕСТ 1: БАЗОВЫЙ ==========

def test_quiz_single(quiz_single):
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    result = quiz_single.export()
    
    expected = """12345678!@# QUIZ

## Выбор одного

2 + 3 = ?

A. 5
B. -5
C. 0
D. 55

ANSWER: A

CONFIG
score: 1"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


def test_quiz_multiple(quiz_multiple):
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    result = quiz_multiple.export()
    
    expected = """12345678!@# QUIZ

## Выбор нескольких

? = 12

A. 6 * 2
B. 7 - 18
C. 1 + 2
D. 9 + 3

ANSWER: A, D

CONFIG
score: 2"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


# ========== ТЕСТ 2: STEP_BEGIN ==========

@pytest.mark.parametrize("step_begin", ['##', '12345678!@#', '##########', '###', ''])
def test_step_begin_variations(quiz_single, step_begin):
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = step_begin
    result = quiz_single.export()
    expected_prefix = f"{step_begin} QUIZ"
    settings.STEP_BEGIN = original
    assert result.startswith(expected_prefix)


# ========== ТЕСТ 3: БЕЗ ЗАГОЛОВКА ==========

def test_no_title():
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Чему равно 2 + 3?</p>',
            'source': {
                'options': [{'is_correct': True, 'text': '<p>5</p>'}],
                'is_multiple_choice': False
            }
        },
        'cost': 1
    }, 5)
    
    result = exporter.export()
    
    expected = """12345678!@# QUIZ

Чему равно 2 + 3?

A. 5

ANSWER: A

CONFIG
score: 1"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


# ========== ТЕСТ 4: LaTeX ==========

def test_latex_in_condition():
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Чему равно \\(e=mc^2\\)?</p>',
            'source': {
                'options': [{'is_correct': True, 'text': '<p>Формула</p>'}],
                'is_multiple_choice': False
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """12345678!@# QUIZ

Чему равно $e=mc^2$?

A. Формула

ANSWER: A

CONFIG
score: 1"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


def test_latex_in_options():
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Выберите функции</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p>$sin(x)$</p>'},
                    {'is_correct': True, 'text': '<p>$x^2$</p>'}
                ],
                'is_multiple_choice': True
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """12345678!@# QUIZ

Выберите функции

A. $sin(x)$
B. $x^2$

ANSWER: A, B

CONFIG
score: 1"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


# ========== ТЕСТ 5: GET_EXPORTER ==========

def test_get_exporter():
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    step_data = {
        'block': {
            'name': 'choice',
            'text': '<p>Test</p>',
            'source': {'options': []}
        }
    }
    
    exporter = get_exporter(step_data, 1)
    settings.STEP_BEGIN = original
    assert isinstance(exporter, QuizDump)


# ========== ТЕСТ 6: МНОГО ВАРИАНТОВ ==========

def test_many_options():
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = '12345678!@#'
    
    options = []
    for i in range(26):
        options.append({
            'is_correct': (i == 0),
            'text': f'<p>Вариант {chr(65+i)}</p>'
        })
    
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<h2>Тест</h2>',
            'source': {
                'options': options,
                'is_multiple_choice': False
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """12345678!@# QUIZ

## Тест

A. Вариант A
B. Вариант B
C. Вариант C
D. Вариант D
E. Вариант E
F. Вариант F
G. Вариант G
H. Вариант H
I. Вариант I
J. Вариант J
K. Вариант K
L. Вариант L
M. Вариант M
N. Вариант N
O. Вариант O
P. Вариант P
Q. Вариант Q
R. Вариант R
S. Вариант S
T. Вариант T
U. Вариант U
V. Вариант V
W. Вариант W
X. Вариант X
Y. Вариант Y
Z. Вариант Z

ANSWER: A

CONFIG
score: 1"""
    
    settings.STEP_BEGIN = original
    assert result.strip() == expected.strip()


# ========== ТЕСТ 7: ВОССТАНОВЛЕНИЕ STEP_BEGIN ==========

def test_settings_restored():
    """Проверяем, что STEP_BEGIN восстанавливается"""
    original = settings.STEP_BEGIN
    
    settings.STEP_BEGIN = 'TEST_VALUE'
    assert settings.STEP_BEGIN == 'TEST_VALUE'
    settings.STEP_BEGIN = original
    