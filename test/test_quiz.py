from src.step_quiz import ParseSchemaStepQuiz, StepQuiz


def test_step_quiz():
    text = """
Условие

A. variant1
B. variant2
C. variant 3

ANSWER: B
"""
    expected_res = {
        'text': 'Условие',
        'variants': [{'letter': 'A', 'text': ' variant1'},
                     {'letter': 'B', 'text': ' variant2'},
                     {'letter': 'C', 'text': ' variant 3'}],
        'answer': ['B']
    }
    res = ParseSchemaStepQuiz.step_quiz().parseString(text).as_dict()
    print(f'\nParseSchemaStepQuiz.step_quiz: {res=}')
    assert res == expected_res

def test_step_quiz_multiple_choice():
    text = """
Условие

A. variant1
B. variant2
C. variant 3

ANSWER: A, C
CONFIG
shuffle: false
"""
    expected_res = {
        'text': 'Условие',
        'variants': [{'letter': 'A', 'text': ' variant1'},
                     {'letter': 'B', 'text': ' variant2'},
                     {'letter': 'C', 'text': ' variant 3'}],
        'answer': ['A', 'C'],
        'config': {'shuffle': 'false'}
    }
    res = ParseSchemaStepQuiz.step_quiz().parseString(text).as_dict()
    print(f'\nParseSchemaStepQuiz.step_quiz: {res=}')
    assert res == expected_res

def test_step_quoted():
    text = """
Условие до.
```
Q. Пример кода
```
Условие после.

A. 
variant1
B. 
```python
print('variant2')
```
C. <code>
if x > 0:
    print('x > 0')
</code>

ANSWER: B
CONFIG:
shuffle: false
"""
    expected_res = {
        'text': 'Условие',
        'variants': [{'letter': 'A', 'text': ' variant1'},
                     {'letter': 'B', 'text': ' variant2'},
                     {'letter': 'C', 'text': ' variant 3'}],
        'answer': ['B'],
        'config': {'shuffle': 'false'}
    }
    res = ParseSchemaStepQuiz.step_quiz().parseString(text).as_dict()
    print(f'\nParseSchemaStepQuiz.step_quiz: {res=}')
    # assert res == expected_res


def test_config_score_applied_to_cost():
    """CONFIG score должен менять стоимость шага (cost), а не несуществующее поле score."""
    text = """
Условие

A. variant1
B. variant2

ANSWER: B
CONFIG
score: 7
"""
    step = StepQuiz(header='')
    step.parse(text)

    res = step.to_dict()

    assert res['stepSource']['cost'] == 7
    assert 'score' not in res['stepSource']


def test_default_cost_without_score_config():
    """Без CONFIG score стоимость шага берется из StepQuiz.DEFAULT_SCORE."""
    text = """
Условие

A. variant1
B. variant2

ANSWER: A
"""
    step = StepQuiz(header='')
    step.parse(text)

    res = step.to_dict()

    assert res['stepSource']['cost'] == StepQuiz.DEFAULT_SCORE
    assert 'score' not in res['stepSource']
