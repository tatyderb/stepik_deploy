from src.lesson import Lesson
from src.markdown_parsing import ParseSchema

text = \
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


def test_split_by_h2():

    lines = text.splitlines()
    lesson = Lesson()
    config, steps = lesson.split_lines_by_h2_and_parse_steps(lines[2:])
    print(config)
    print(lesson.steps)
    assert config == {'lesson': '123', 'lang': 'python3.10'}
    print(steps)
    assert steps[0].lines == step1.splitlines()
    assert steps[1].lines == step2.splitlines()
    assert steps[2].lines == step3.splitlines()

def test_split_document():

    # res = ParseSchema.document().parseString(text)
    res = ParseSchema.parse_document(text)
    print(f'\n{res=}')
    for item in res:
        print(f'{item=}')
        # print(f'{item.h1_header=}')
        # print(f'{item.text=}')



def test_parse_lesson():
    lines = text.splitlines()
    lesson = Lesson()
    lesson.parse_markdown(lines)
    assert lesson.lesson_id == 123
    assert len(lesson.steps) == 3
