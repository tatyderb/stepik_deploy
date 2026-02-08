import pytest

from src.step_table import ParseSchemaStepTable


text1 = """
Условие
TABLE
| Ряды:      | Первая колонка | Вторая колонка |
|------------|----------------|----------------|
| Первый ряд | a              | c              |
| Второй ряд | b              | d              |
| Третий ряд | b              | d              |
"""

text2 = """
Условие
TABLE
| Ряды:      | Первая колонка | Вторая колонка |
|------------|----------------|----------------|
| Первый ряд | a              | c              |
| Второй ряд | b              | d              |
| Третий ряд | b              | d              |
CONFIG
score: 3
"""


def test_parse_step_table():
    res = ParseSchemaStepTable.parse_step_table(text1)
    expected_dict = {'text': 'Условие',
                     'table_rows': [
                         ['Ряды:', 'Первая колонка', 'Вторая колонка'],
                         ['------------', '----------------', '----------------'],
                         ['Первый ряд', 'a', 'c'], ['Второй ряд', 'b', 'd'],
                         ['Третий ряд', 'b', 'd']]}
    assert res == expected_dict
    res = ParseSchemaStepTable.parse_step_table(text2)
    expected_dict = {'text': 'Условие',
                     'table_rows': [
                         ['Ряды:', 'Первая колонка', 'Вторая колонка'],
                         ['------------', '----------------', '----------------'],
                         ['Первый ряд', 'a', 'c'], ['Второй ряд', 'b', 'd'],
                         ['Третий ряд', 'b', 'd']],
                     'config': {'score': '3'}}
    assert res == expected_dict
