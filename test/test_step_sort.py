import pytest

from src.step_sort import ParseSchemaStepSort


text1 = '''
Расставьте времена года по порядку, начиная  с зимы.

SORT
Зима
====
Весна
====
Лето
====
Осень
====
'''

text2 = '''
Расставьте времена года по порядку, начиная  с зимы.

SORT
Зима
====
Весна
====
Лето
====
Осень
====

CONFIG
html: false
'''


text3 = '''
SORT
====
'''

text4 = '''
Расположите группы по среднему размеру от меньшего к большему
SORT
<ul>
<li>Холм</li>
<li>Овраг</li>
<li>Утес</li>
</ul>
====
<ul>
<li>Горный хребет</li>
<li>Плато</li>
<li>Речная долина</li>
</ul>
====
<ul>
<li>Материк</li>
<li>Тектоническая плита</li>
<li>Океан</li>
</ul>

CONFIG
html: true
'''

text5 = '''
Условие
SORT
Первый пункт
====
Второй пункт
====
CONFIG
score: 3
'''

def test_parse_step_essay():
    res = ParseSchemaStepSort.parse_step_sort(text1)
    print(f'\nparse_step_sort: {res=}')
    expected_dict = {'text': 'Расставьте времена года по порядку, начиная  с зимы.', 'options': [{'text': 'Зима'}, {'text': 'Весна'}, {'text': 'Лето'}, {'text': 'Осень'}]}
    assert res == expected_dict
    res = ParseSchemaStepSort.parse_step_sort(text2)
    print(f'\nparse_step_sort: {res=}')
    expected_dict = {'text': 'Расставьте времена года по порядку, начиная  с зимы.', 'options': [{'text': 'Зима'}, {'text': 'Весна'}, {'text': 'Лето'}, {'text': 'Осень'}], 'config': {'html': 'false'}}
    assert res == expected_dict
    res = ParseSchemaStepSort.parse_step_sort(text3)
    print(f'\nparse_step_sort: {res=}')
    expected_dict = {'text': '', 'options': [{'text': ''}]}
    assert res == expected_dict
    res = ParseSchemaStepSort.parse_step_sort(text4)
    print(f'\nparse_step_sort: {res=}')
    expected_dict = {'text': 'Расположите группы по среднему размеру от меньшего к большему', 'options': [{'text': '<ul>\n<li>Холм</li>\n<li>Овраг</li>\n<li>Утес</li>\n</ul>'}, {'text': '<ul>\n<li>Горный хребет</li>\n<li>Плато</li>\n<li>Речная долина</li>\n</ul>'}]}
    assert res == expected_dict
    res = ParseSchemaStepSort.parse_step_sort(text5)
    print(f'\nparse_step_sort: {res=}')
    expected_dict = {'text': 'Условие', 'options': [{'text': 'Первый пункт'}, {'text': 'Второй пункт'}], 'config': {'score': '3'}}
    assert res == expected_dict


if __name__ == "__main__":
    res = ParseSchemaStepSort.parse_step_sort(text1)
    print(res)