import pytest

from src.step_string import ParseSchemaStepString

text1 = '''
Здесь условие
ANSWER: Ответ
CONFIG
score: 2
'''

text2 = '''
Живая оболочка Земли
ANSWER: биосфера
'''

text3 = '''
Вставьте следующий абзац стихотворения
По вечерам над ресторанами
Горячий воздух дик и глух,
И правит окриками пьяными
Весенний и тлетворный дух.
ANSWER: 
Вдали, над пылью переулочной,
Над скукой загородных дач,
Чуть золотится крендель булочной,
И раздается детский плач.
CONFIG
score: 5
'''


text4 = '''
Как называется шахматная фигура, которая ходит по вертикали и горизонтали?
ANSWER: ладья
CONFIG
score: 2
use_re: false
match_substring: false
is_text_disabled: false
is_file_disabled: true
'''


res = ParseSchemaStepString.parse_step_string(text2)
print(f'\nparse_step_string: {res=}')

def test_parse_step_number():
    res = ParseSchemaStepString.parse_step_string(text1)
    expected_dict = {'text': 'Здесь условие', 
                     'answer': 'Ответ', 
                     'config': {'score': '2'}}
    
    assert res == expected_dict
    res = ParseSchemaStepString.parse_step_string(text2)
    
    expected_dict = {'text': 'Живая оболочка Земли', 
                     'answer': 'биосфера'}
    assert res == expected_dict

    res = ParseSchemaStepString.parse_step_string(text3)
    expected_dict = {'text': 'Вставьте следующий абзац стихотворения\nПо вечерам над ресторанами\nГорячий воздух дик и глух,\nИ правит окриками пьяными\nВесенний и тлетворный дух.', 
                     'answer': 'Вдали, над пылью переулочной,\nНад скукой загородных дач,\nЧуть золотится крендель булочной,\nИ раздается детский плач.', 
                     'config': {'score': '5'}}
    assert res == expected_dict

    res = ParseSchemaStepString.parse_step_string(text4)
    expected_dict = {'text': 'Как называется шахматная фигура, которая ходит по вертикали и горизонтали?', 
                     'answer': 'ладья', 
                     'config': {
                         'is_file_disabled': 'true', 
                         'is_text_disabled': 'false', 
                         'match_substring': 'false',
                         'is_text_disabled': 'false',
                         'is_file_disabled': 'true',
                         'use_re': 'false',
                         'score': '2'}}
    assert res == expected_dict

  
