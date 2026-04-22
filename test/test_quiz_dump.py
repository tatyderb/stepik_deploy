"""
Тесты для дампа QUIZ шагов
"""

import pytest
from src.export.dump import QuizDump, get_exporter


pytestmark = pytest.mark.step_begin("---1234")


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
                'is_multiple_choice': False,
                'is_html_enabled': True
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
                'is_multiple_choice': True,
                'is_html_enabled': True
            }
        },
        'cost': 2
    }, 1)


# ========== ТЕСТ 1: БАЗОВЫЙ ==========

def test_quiz_single(quiz_single):
    result = quiz_single.export()
    
    expected = """---1234 QUIZ

## Выбор одного

2 + 3 = ?

A. 5
B. -5
C. 0
D. 55

ANSWER: A

CONFIG
score: 1
"""

    assert result.strip() == expected.strip()


def test_quiz_multiple(quiz_multiple):
    result = quiz_multiple.export()
    
    expected = """---1234 QUIZ

## Выбор нескольких

? = 12

A. 6 * 2
B. 7 - 18
C. 1 + 2
D. 9 + 3

ANSWER: A, D

CONFIG
score: 2
"""

    assert result.strip() == expected.strip()


# ========== ТЕСТ 2: STEP_BEGIN ==========

@pytest.mark.parametrize("step_begin", ['##', '12345678!@#', '##########', '###', ''])
def test_step_begin_variations(quiz_single, step_begin):
    from src.export.dump import settings
    original = settings.STEP_BEGIN
    settings.STEP_BEGIN = step_begin
    result = quiz_single.export()
    expected_prefix = f"{step_begin} QUIZ"
    settings.STEP_BEGIN = original
    assert result.startswith(expected_prefix)


# ========== ТЕСТ 3: БЕЗ ЗАГОЛОВКА ==========

def test_no_title():
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Чему равно 2 + 3?</p>',
            'source': {
                'options': [{'is_correct': True, 'text': '<p>5</p>'}],
                'is_multiple_choice': False,
                'is_html_enabled': True
            }
        },
        'cost': 1
    }, 5)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

Чему равно 2 + 3?

A. 5

ANSWER: A

CONFIG
score: 1
"""

    assert result.strip() == expected.strip()


# ========== ТЕСТ 4: LaTeX ==========

def test_latex_in_condition():
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Чему равно \\(e=mc^2\\)?</p>',
            'source': {
                'options': [{'is_correct': True, 'text': '<p>Формула</p>'}],
                'is_multiple_choice': False,
                'is_html_enabled': True
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

Чему равно $e=mc^2$?

A. Формула

ANSWER: A

CONFIG
score: 1
"""

    assert result.strip() == expected.strip()


def test_latex_in_options():
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<p>Выберите функции</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p>$sin(x)$</p>'},
                    {'is_correct': True, 'text': '<p>$x^2$</p>'}
                ],
                'is_multiple_choice': True,
                'is_html_enabled': True
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

Выберите функции

A. $sin(x)$
B. $x^2$

ANSWER: A, B

CONFIG
score: 1
"""

    assert result.strip() == expected.strip()


# ========== ТЕСТ 5: GET_EXPORTER ==========

def test_get_exporter():
    step_data = {
        'block': {
            'name': 'choice',
            'text': '<p>Test</p>',
            'source': {
                'options': [],
                'is_html_enabled': True
            }
        }
    }
    
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, QuizDump)


# ========== ТЕСТ 6: МНОГО ВАРИАНТОВ ==========

def test_many_options():
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
                'is_multiple_choice': False,
                'is_html_enabled': True
            }
        },
        'cost': 1
    }, 1)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

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
score: 1
"""

    assert result.strip() == expected.strip()


# ========== ТЕСТ 7: HTML БЕЗ КОНВЕРТАЦИИ ==========

def test_html_disabled_options():
    """Тест: is_html_enabled=False - HTML теги должны быть удалены"""
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<h2>HTML отключен</h2><p>Выберите ответ</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p><strong>Верный</strong> ответ</p>'},
                    {'is_correct': False, 'text': '<p><em>Неверный</em> ответ</p>'}
                ],
                'is_multiple_choice': False,
                'is_html_enabled': False
            }
        },
        'cost': 2
    }, 1)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

## HTML отключен

Выберите ответ

A. Верный ответ
B. Неверный ответ

ANSWER: A

CONFIG
score: 2
"""

    assert result.strip() == expected.strip()


# ========== ТЕСТ 8: HTML С КОНВЕРТАЦИЕЙ ==========

def test_html_enabled_options():
    """Тест: is_html_enabled=True - HTML конвертируется в Markdown"""
    exporter = QuizDump({
        'block': {
            'name': 'choice',
            'text': '<h2>HTML в вариантах</h2><p>Выберите ответ</p>',
            'source': {
                'options': [
                    {'is_correct': True, 'text': '<p><strong>Верный</strong> ответ</p>'},
                    {'is_correct': False, 'text': '<p><em>Неверный</em> ответ</p>'},
                    {'is_correct': False, 'text': '<p><a href="https://example.com">Ссылка</a></p>'}
                ],
                'is_multiple_choice': False,
                'is_html_enabled': True
            }
        },
        'cost': 3
    }, 1)
    
    result = exporter.export()
    
    expected = """---1234 QUIZ

## HTML в вариантах

Выберите ответ

A. **Верный** ответ
B. *Неверный* ответ
C. [Ссылка](https://example.com)

ANSWER: A

CONFIG
score: 3
"""

    assert result.strip() == expected.strip()