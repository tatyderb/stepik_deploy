import pytest

from src.step_essay import ParseSchemaStepEssay


text1 = '''
Условие задачи.
Много строк
CONFIG
score: 5
'''

text2 = '''
Дана трапеция ABCD с основаниями AD и BC.  Диагональ BD разбивает её на два равнобедренных треугольника с основаниями AD и CD.

а) Докажите, что луч AC — биссектриса угла BAD.

б) Найдите CD, если известны диагонали трапеции: AC=12 и BD=6,5.
'''


text3 = '''
Текстовое описание задания
CONFIG
score: 5
is_attachments_enabled: false,
is_html_enabled: true,
manual_scoring: false
'''


def test_parse_step_essay():
    res = ParseSchemaStepEssay.parse_step_essay(text1)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {'text': 'Условие задачи.\nМного строк', 'config': {'score': '5'}}
    assert res == expected_dict
    res = ParseSchemaStepEssay.parse_step_essay(text2)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {'text': 'Дана трапеция ABCD с основаниями AD и BC.  Диагональ BD разбивает её на два равнобедренных треугольника с основаниями AD и CD.\n\nа) Докажите, что луч AC — биссектриса угла BAD.\n\nб) Найдите CD, если известны диагонали трапеции: AC=12 и BD=6,5.'}
    assert res == expected_dict
    res = ParseSchemaStepEssay.parse_step_essay(text3)
    print(f'\nparse_step_number: {res=}')
    expected_dict = {'text': 'Текстовое описание задания', 'config': {'score': '5', 'is_attachments_enabled': 'false', 'is_html_enabled': 'true', 'manual_scoring': 'false'}}
    assert res == expected_dict


if __name__ == "__main__":
    res = ParseSchemaStepEssay.parse_step_essay(text3)
    print(f'\nparse_step_essay: {res=}')