import pytest

from src.lesson import Lesson
from src.markdown_parsing import ParseSchema

lesson_text = \
'''# Урок 1
lesson = 123
lang = python3.10

## Шаг 1
Содержимое шага один.
## SKIP Шаг 2 пропускаем
Второй шаг.
Пишем много чего интересного

## TEXT Шаг третий

Тут много пустых строк.

Которые нужно тоже обработать.    
    '''
step1 = 'Содержимое шага один.'
step2 = '''Второй шаг.
Пишем много чего интересного

'''
step3 = '''
Тут много пустых строк.

Которые нужно тоже обработать.    
    '''


# def test_split_by_h2():
#
#     lines = text.splitlines()
#     lesson = Lesson()
#     config, steps = lesson.split_lines_by_h2_and_parse_steps(lines[2:])
#     print(config)
#     print(lesson.steps)
#     assert config == {'lesson': '123', 'lang': 'python3.10'}
#     print(steps)
#     assert steps[0].lines == step1.splitlines()
#     assert steps[1].lines == step2.splitlines()
#     assert steps[2].lines == step3.splitlines()

def test_split_document():

    # res = ParseSchema.document().parseString(text)
    res = ParseSchema.parse_document(lesson_text)
    # print(f'\n{res=}')
    # for item in res:
    #     print(f'{item=}')
    assert res['title'] == 'Урок 1'
    assert res['variables'] ==  {'lesson': '123', 'lang': 'python3.10'}
    assert len(res['steps']) == 3


@pytest.mark.parametrize('text, expected_dict', [
    ('\nlesson = 123\nlang = python3.10\n', {'lesson':'123', 'lang': 'python3.10' }),
    ('\nlesson = 123\n\n', {'lesson':'123'}),
    ('lang = python3.10\n', {'lang': 'python3.10' }),
    ('\n\n', { }),
    ]
)
def test_parse_lesson(text, expected_dict):
    res = ParseSchema.parse_variables(text)
    # print(f'\n{res=}')
    # print(f'\n{res.as_dict()=}')
    assert res == expected_dict


def test_quoted_into_text():
    # pp.Quoted нормально вычленяет вставки
    quoted = ParseSchema.quoted
    res = quoted().parseString( """```закавыченный 
    текст```""")
    # print(res.dump())
    assert res.as_list() == ['```закавыченный \n    текст```']

    # тестировали как разбирать заковыченный текст, чтобы внутри него не разбирались теги
    # import pyparsing as pp
    # h2_header = pp.LineStart() + "##" + pp.Suppress(pp.White()) + pp.restOfLine("h2_header")  # Заголовок уровня 2
    #
    # # Текст до следующего заголовка или конца документа с учетом ## внутри вставок кода
    # text_bound = quoted | h2_header | pp.stringEnd
    # text_part = pp.SkipTo(text_bound)
    # text = (text_part + pp.ZeroOrMore(quoted + text_part))("text")
    # text.setParseAction(lambda t: ''.join(t.text))
#
#     s = """до кавычек
# ```
# внутри
# строки
# ```
# после
# """
#     res = text.parseString(s)
#     print(res.dump())

    input = """# урок с кавычками
lesson = 123

## Шаг1 без кавычек

Текст без кавычек.

## Шаг2 с кавычками

До кавычек
```
print('hello')
```
После кавычек

## Шаг3 с ## внутри кавычек
До кавычек
```
## Ложный заголовок
print('hello')
```
После кавычек


"""
    expected_dict = {
        'title': 'урок с кавычками',
        'variables': {'lesson': '123'},
        'steps': [
            {'h2': 'Шаг1 без кавычек', 'text': '\n\nТекст без кавычек.\n'},
            {'h2': 'Шаг2 с кавычками', 'text': "\n\nДо кавычек```\nprint('hello')\n```\nПосле кавычек\n"},
            {'h2': 'Шаг3 с ## внутри кавычек', 'text': "\nДо кавычек```\n## Ложный заголовок\nprint('hello')\n```\nПосле кавычек"}
        ]}
    res = ParseSchema.parse_document(input)
    # print(res)
    assert res == expected_dict

