import pytest

from src.step_match import ParseSchemaStepMatch


text1 = '''
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
is_randomize: false
html: false
'''

text2 = '''Условие
MATCH
Пункт 1
----
Значение, соответствующее пункту 1
====
Пункт 2
----
Значение, соответствующее пункту 2
====
Пункт 3
----
Значение, соответствующее пункту 3
====
CONFIG
score: 3'''


text3 = '''
Добавлено перемешивание в первом столбце (is_randomize)
Изменены баллы за задачу (score)

Как называют детенышей животных?

MATCH
Корова
----
Телёнок
====
Лошадь
----
Жеребёнок
====
Овца
----
Ягнёнок
====

CONFIG
is_randomize: true
score: 3

'''


def test_parse_step_match():
    res = ParseSchemaStepMatch.parse_step_match(text1)
    print(f'\nparse_step_match: {res=}')
    expected_dict = {'text': 'Кто автор произведения?\n', 'pairs': [{'first': 'Муму', 'second': 'Тургенев И.С.'}, {
        'first': 'Война и мир', 'second': 'Толстой Л.Н.'}, {'first': 'Бородино', 'second': 'Лермонтов М.Ю.'}], 'config': {'is_randomize': 'false', 'html': 'false'}}
    assert res == expected_dict
    res = ParseSchemaStepMatch.parse_step_match(text2)
    print(f'\nparse_step_match: {res=}')
    expected_dict = {'text': 'Условие\n', 'pairs': [{'first': 'Пункт 1', 'second': 'Значение, соответствующее пункту 1'}, {
        'first': 'Пункт 2', 'second': 'Значение, соответствующее пункту 2'}, {'first': 'Пункт 3', 'second': 'Значение, соответствующее пункту 3'}], 'config': {'score': '3'}}
    assert res == expected_dict
    res = ParseSchemaStepMatch.parse_step_match(text3)
    print(f'\nparse_step_match: {res=}')
    expected_dict = {'text': 'Добавлено перемешивание в первом столбце (is_randomize)\nИзменены баллы за задачу (score)\n\nКак называют детенышей животных?\n', 'pairs': [
        {'first': 'Корова', 'second': 'Телёнок'}, {'first': 'Лошадь', 'second': 'Жеребёнок'}, {'first': 'Овца', 'second': 'Ягнёнок'}], 'config': {'is_randomize': 'true', 'score': '3'}}
    assert res == expected_dict
