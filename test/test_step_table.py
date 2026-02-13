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

text3 = """
Условие
```
TABLE
| Ряды:      | internal с1 | internal с2 |
|------------|-------------|-------------|
| internal r1 | a          | c             |
| internal r1 | b          | d             |
```
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
    expected_dict = {'text': 'Условие\n',
                     'table_rows': [
                         ['Ряды:', 'Первая колонка', 'Вторая колонка'],
                         ['------------', '----------------', '----------------'],
                         ['Первый ряд', 'a', 'c'], ['Второй ряд', 'b', 'd'],
                         ['Третий ряд', 'b', 'd']]}
    assert res == expected_dict
    res = ParseSchemaStepTable.parse_step_table(text2)
    expected_dict = {'text': 'Условие\n',
                     'table_rows': [
                         ['Ряды:', 'Первая колонка', 'Вторая колонка'],
                         ['------------', '----------------', '----------------'],
                         ['Первый ряд', 'a', 'c'], ['Второй ряд', 'b', 'd'],
                         ['Третий ряд', 'b', 'd']],
                     'config': {'score': '3'}}
    assert res == expected_dict
    res = ParseSchemaStepTable.parse_step_table(text3)
    expected_dict = {'text': '''Условие```
TABLE
| Ряды:      | internal с1 | internal с2 |
|------------|-------------|-------------|
| internal r1 | a          | c             |
| internal r1 | b          | d             |
```
''',
                     'table_rows': [
                         ['Ряды:', 'Первая колонка', 'Вторая колонка'],
                         ['------------', '----------------', '----------------'],
                         ['Первый ряд', 'a', 'c'], ['Второй ряд', 'b', 'd'],
                         ['Третий ряд', 'b', 'd']],
                     'config': {'score': '3'}}
    assert res == expected_dict
