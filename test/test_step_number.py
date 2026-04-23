import pytest

from src.step_number import ParseSchemaStepNumber


# @pytest.mark.parametrize('text, ok, number, accuracy', [
#     ('ANSWER: 123', True, 123, 0),
    # ('ANSWER: -123', True, -123, 0),
    # ('ANSWER: 3.14', True, 3.14, 0),
    # ('ANSWER: -3.14', True, -3.14, 0),
    # ('ANSWER: 123 +-7', True, 123, 7),
    # ('ANSWER: 123 +- 5', True, 123, 5),
    # ('ANSWER: -123 +-1', True, -123, 1),
    # ('ANSWER: 3.14 +-0.1', True, 3.14, 0.1),
    # ('ANSWER: -234.567 +-0.002', True, -234.567, 0.002),
# ])
# def test_parse_step_number_answer(text, ok, number, accuracy):
#     res_ok, res_number, res_accuracy = ParseSchemaStepNumber.parse_answer(text)
#     assert res_ok == ok
#     assert res_number == number
#     assert res_accuracy == accuracy

@pytest.mark.parametrize('text, expected_dict', [
    ('ANSWER: 123', {'answer': 123, 'accuracy': 0}),
    ('ANSWER: -123', {'answer': -123, 'accuracy': 0}),
    ('ANSWER: 3.14', {'answer': 3.14, 'accuracy': 0}),
    ('ANSWER: -3.14', {'answer': -3.14, 'accuracy': 0}),
    ('ANSWER: 123 +-7', {'answer': 123, 'accuracy': 7}),
    ('ANSWER: 123 +- 5', {'answer': 123, 'accuracy': 5}),
    ('ANSWER: -123 +-1', {'answer': -123, 'accuracy': 1}),
    ('ANSWER: 123 +-0.1', {'answer': 123, 'accuracy': 0.1}),
    ('ANSWER: 3.14 +-0.1', {'answer': 3.14, 'accuracy': 0.1}),
    ('ANSWER: 123.14 +-0.002', {'answer': 123.14, 'accuracy': 0.002}),
])
def test_answer(text, expected_dict):
    res = ParseSchemaStepNumber.answer().parse_string(text)
    print(f'{res=}')

text1 = '''
Условие задачи.
Много строк
ANSWER: 3.14 +-0.1
CONFIG
score: 5
'''

text2 = """
Условие задачи.
```python
ANSWER: 5
```
Между блоками.
```cpp
ANSWER: 6
```
Постусловие.
ANSWER: 7
"""

text3 = """
Найдите x: x^2-6x+5=0

ANSWER = 1
ANSWER = 5
"""

text4 = """
Найдите ошибку в задаче, замените на правильный ответ:
```
## NUMBER

Найдите x: x^2-6x+5=0

ANSWER = 1
ANSWER = -3
```
ANSWER = 5
"""


def test_parse_step_number():
    res = ParseSchemaStepNumber.parse_step_number(text1)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {'text': 'Условие задачи.\nМного строк', 'answer': [{'number': 3.14, 'accuracy': 0.1}], 'config': {'score': '5'}}
    assert res == expected_dict

    res = ParseSchemaStepNumber.parse_step_number(text2)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {
        'text': 'Условие задачи.\n```python\nANSWER: 5\n```\nМежду блоками.\n```cpp\nANSWER: 6\n```\nПостусловие.',
        'answer': [{'number': 7, 'accuracy': 0}]
    }
    assert res == expected_dict
    res = ParseSchemaStepNumber.parse_step_number(text3)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {
        'text': 'Найдите x: x^2-6x+5=0',
        'answer': [{'number': 1, 'accuracy': 0}, {'number': 5, 'accuracy': 0}]
    }
    assert res == expected_dict
    res = ParseSchemaStepNumber.parse_step_number(text4)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {
        'text': 'Найдите ошибку в задаче, замените на правильный ответ:\n```\n## NUMBER\n\nНайдите x: x^2-6x+5=0\n\nANSWER = 1\nANSWER = -3\n```\n',
        'answer': [{'number': 5, 'accuracy': 0}]
    }
    assert res == expected_dict


def test_sections():
    """ Исследование: Обязательные и необязательные элементы в произвольном порядке"""
    import pyparsing as pp
    required_a  = pp.Literal('aaa')
    required_c  = pp.Literal('ccc')
    optional = pp.Opt(pp.Literal('bbb'))
    schema = required_a & optional & required_c

    schema.run_tests("""\
    # all words
    aaa bbb ccc
    
    # chaotic
    bbb ccc aaa
    
    # no optional
    ccc aaa
    
    """)

    # первым должен идти обязательный aaa
    schema2 = required_a + (required_c & optional)

    schema2.run_tests("""\
    # all words
    aaa bbb ccc

    # chaotic
    aaa ccc bbb

    # no optional
    aaa ccc
    
    # wrong: no aaa
    bbb ccc
    
    # wrong: aaa not first
    bbb aaa ccc
    """)


