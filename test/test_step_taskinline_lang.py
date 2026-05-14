"""
Проверяем, что lang в TASKINLINE правильно обрабатывается.
1. Если задано TEMPLATE, на lang не обращаем внимание, темплита копируется как есть (используется для задач на несколько языков)
2. CONFIG lang='c_valgrind' без других частей, просто добавляем ::c_valgrind
3. CONFIG lang='c_valgrind' с HEADER, FOOTER, CODE
4. CONFIG lang='all' без других частей, пустая вкладка
5. CONFIG lang='all' с HEADER, FOOTER, CODE - сообщение об ошибке (нет) или отсутствие темплиты (да)
6. lesson lang='c_valgrind' без CONFIG - получаем c_valgrind
7. lesson lang='c_valgrind' с CONFIG lang=haskel - получаем haskel
8. lesson lang='c_valgrind' с CONFIG lang=all - получаем пустую вкладку
9. lesson lang='all' с CONFIG lang=haskel - получаем haskel
"""
import json

from src.lesson import Lesson

# Кирпичики как в файле test_step_taskinline.py
text_task_base = """
## TASKINLINE Задача

Даны два целых числа на одной строке через пробел. Напечатайте их сумму.

TEST
2 3
----
5
====
-17 -23
----
-40
====    
"""
expected_dict_base = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
                 'tests': ['2 3', '5', '-17 -23', '-40']}

text_header_footer = """
HEADER
#include <stdio.h>
    // нужно сохранять отступы в начале строки
int module(int x);
FOOTER
int main()
{
    int x;
    scanf("%d", &x);
    printf("%d\n", module(x));
    return 0;
}
CODE
int module(int x) {
    // здесь нужно написать код
}
"""
expected_header_footer_dict = {
     'header': '#include <stdio.h>\n    // нужно сохранять отступы в начале строки\nint module(int x);\n',
     'footer': 'int main()\n{\n    int x;\n    scanf("%d", &x);\n    printf("%d\n", module(x));\n    return 0;\n}\n',
     'code': 'int module(int x) {\n    // здесь нужно написать код\n}\n'
}
# то же самое в виде текста
expected_header_footer_text = \
     '::code\n' + expected_header_footer_dict['code'] + \
     '::header\n'+ expected_header_footer_dict['header'] + \
     '::footer\n' + expected_header_footer_dict['footer']

expected_template_text = """
::c
::header
#include <stdio.h>
int module(int x);
::footer
int main()
{
  int x;
  scanf("%d", &x);
  printf("%d\n", module(x));
  return 0;
}
::code
int module(int x) {
  // здесь нужно написать код
}

::c++
::header
#include <iostream>
int module(int x);
::footer
int main()
{
  int x;
  std::cin >> x;
  std::cout << module(x)) << std::endl;
  return 0;
}
::code
int module(int x) {
  // здесь нужно написать код
}"""


lesson_text_empty = """
# Заголовок урока

lesson = 12345
"""

lesson_text_lang = """
# Заголовок урока

lesson = 12345
lang = c_valgrind
"""

def test_template():
    """1. Если задано TEMPLATE, на lang не обращаем внимание,
    темплита копируется как есть (используется для задач на несколько языков)
    """
    text = '\n'.join([
        lesson_text_lang,
        text_task_base,
        "TEMPLATE",
        expected_template_text,
        "CONFIG",
        "lang=haskel"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    assert source['templates_data'] == expected_template_text


def test_config_lang_only():
    """2. CONFIG lang='haskel' без других частей, просто добавляем ::haskel"""
    text = '\n'.join([
        lesson_text_lang,
        text_task_base,
        "CONFIG",
        "lang=haskel"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == "::haskel\n"

def test_config_lang_only_header():
    """3. CONFIG lang='haskel' с HEADER, FOOTER, CODE"""
    text = '\n'.join([
        lesson_text_lang,
        text_task_base,
        text_header_footer,
        "CONFIG",
        "lang=haskel"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    # assert source['templates_data'] == "::haskel\n" expected_header_footer_tuple)
    assert source['templates_data'] == "::haskel\n" + expected_header_footer_text

def test_config_lang_all():
    """4. CONFIG lang='all' без других частей, пустая вкладка"""
    text = '\n'.join([
        lesson_text_lang,
        text_task_base,
        "CONFIG",
        "lang=all"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == ""

def test_config_lang_all_header():
    """5. CONFIG lang='all' с HEADER, FOOTER, CODE - сообщение об ошибке (нет) или отсутствие темплиты (да)"""
    text = '\n'.join([
        lesson_text_lang,
        text_task_base,
        text_header_footer,
        "CONFIG",
        "lang=all"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == ""

def test_lesson_lang():
    """6. lesson lang='c_valgrind' без CONFIG - получаем c_valgrind"""
    text = '\n'.join([
        lesson_text_empty,
        "lang = c_valgrind",
        text_task_base,
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == "::c_valgrind\n"

def test_lesson_config_lang():
    """7. lesson lang='c_valgrind' с CONFIG lang=haskel - получаем haskel"""
    text = '\n'.join([
        lesson_text_empty,
        "lang = c_valgrind",
        text_task_base,
        "CONFIG",
        "lang = haskel"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == "::haskel\n"

def test_lesson_config_lang_all():
    """8. lesson lang='c_valgrind' с CONFIG lang=all - получаем пустую вкладку"""
    text = '\n'.join([
        lesson_text_empty,
        "lang = c_valgrind",
        text_task_base,
        "CONFIG",
        "lang = all"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == ""

def test_lesson_all_config_lang():
    """9. lesson lang='all' с CONFIG lang=haskel - получаем haskel"""
    text = '\n'.join([
        lesson_text_empty,
        "lang = all",
        text_task_base,
        "CONFIG",
        "lang = haskel"
    ])

    lesson = Lesson()
    lesson.parse_markdown(text=text)
    # print(text)

    step = lesson.steps[0]
    res_dict = step.to_dict()
    source = res_dict['stepSource']['block']['source']
    # print(json.dumps(source, indent=2, ensure_ascii=False))
    assert source['templates_data'] == "::haskel\n"

