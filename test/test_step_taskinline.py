from src.step_tasklinline import ParseSchemaStepTaskinline, StepTaskinline

text1 = """
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
expected_res1 = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
                 'tests': ['2 3', '5', '-17 -23', '-40']}

text2 = """
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
CONFIG
lang: c
score: 5
"""
expected_res2 = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
                 'tests': ['2 3', '5', '-17 -23', '-40'],
                 'header': '#include <stdio.h>\n    // нужно сохранять отступы в начале строки\nint module(int x);',
                 'footer': 'int main()\n{\n    int x;\n    scanf("%d", &x);\n    printf("%d\n", module(x));\n    return 0;\n}',
                 'code': 'int module(int x) {\n    // здесь нужно написать код\n}', 'config': {'lang': 'c', 'score': '5'}}

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
}
"""
text3 = "TEMPLATE\n" + expected_template_text
expected_res3 = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
                 'tests': ['2 3', '5', '-17 -23', '-40'],
                 'template': expected_template_text.rstrip()
                 }
def test_step_inline_simple():
    res = ParseSchemaStepTaskinline.step_taskinline().parseString(text1).as_dict()
    print(f'\nParseSchemaStepTaskinline.step_taskinline: \n{res=}')
    assert expected_res1 == res

    res = ParseSchemaStepTaskinline.step_taskinline().parseString(text1 + text2).as_dict()
    print(f'\nParseSchemaStepTaskinline.step_taskinline: \n{res=}')

    assert expected_res2 == res

    res = ParseSchemaStepTaskinline.step_taskinline().parseString(text1 + text3).as_dict()
    print(f'\nParseSchemaStepTaskinline.step_taskinline: \n{res=}')

    assert expected_res3 == res

def test_example_section():
    # все тесты (по умолчанию)
    expected_html = """
<h4>Test #1 input</h4>
<pre>3 2</pre>
<h4>Test #1 output</h4>
<pre>-3 2</pre>
<details><summary>Тестовые данные</summary>

<h4>Test #2 input</h4>
<pre>-3 2</pre>
<h4>Test #2 output</h4>
<pre>3 2</pre>
\n\n<h4>Test #3 input</h4>\n<pre>-10 -7</pre>\n<h4>Test #3 output</h4>\n<pre>10 -7</pre>\n\n\n<h4>Test #4 input</h4>\n<pre>10 -7</pre>\n<h4>Test #4 output</h4>\n<pre>-10 -7</pre>\n\n\n<h4>Test #5 input</h4>\n<pre>0 0</pre>\n<h4>Test #5 output</h4>\n<pre>0 0</pre>\n</details>"""
    tests = [['3 2', '-3 2'], ['-3 2', '3 2'], ['-10 -7', '10 -7'], ['10 -7', '-10 -7'], ['0 0', '0 0']]
    s = StepTaskinline()
    res = s.test_examples(tests, open_tests_number=-1)
    print(f'\n{res=}')
    assert expected_html == res

    # # 3 открытых теста
    expected_html = """
<h4>Test #1 input</h4>
<pre>3 2</pre>
<h4>Test #1 output</h4>
<pre>-3 2</pre>
<details><summary>Тестовые данные</summary>

<h4>Test #2 input</h4>
<pre>-3 2</pre>
<h4>Test #2 output</h4>
<pre>3 2</pre>
\n\n<h4>Test #3 input</h4>\n<pre>-10 -7</pre>\n<h4>Test #3 output</h4>\n<pre>10 -7</pre>\n<p>Остальные тесты закрыты авторами курса.</p>\n</details>"""
    res = s.test_examples(tests, open_tests_number=3)
    print(f'\n{res=}')
    assert expected_html == res

    # Тестов нет
    expected_html = "<details><summary>Тестовые данные</summary>\nДанные закрыты.</details>"
    res = s.test_examples(tests, open_tests_number=0)
    print(f'\n{res=}')
    assert expected_html == res

    expected_html = ''
    res = s.test_examples(tests, open_tests_number=-2)
    print(f'\n{res=}')
    assert expected_html == res



def test_to_dict():
    import json
    step = StepTaskinline(header='')
    step.parse(text1+text3)
    res = step.to_dict()
    print(json.dumps(res, indent=4, ensure_ascii=False))
    
    expected_dict = {
        "stepSource": {
            "reason_of_failure": None,
            "instruction_id": None,
            "has_instruction": False,
            "cost": 10,
            "is_solutions_unlocked": True,
            "solutions_unlocked_attempts": 4,
            "max_submissions_count": 3,
            "has_submissions_restrictions": False,
            "create_date": None,
            "block": {
                "text": "<h2></h2>\n<p>Даны два целых числа на одной строке через пробел. Напечатайте их сумму.</p>",
                "name": "code",
                "video": None,
                "options": None,
                "source": {
                    "code": "\n\ndef check_asis(reply, clue):\n    \"\"\"Сравнение текста, без пробельных символов в конце текста.\"\"\"\n    return reply.strip() == clue.strip()\n        \n        \n# This is a sample Code Challenge\n# Learn more: https://stepik.org/lesson/9172\n# Ask your questions via help@stepik.org\n\ndef generate():\n    return []\n\ndef check(reply, clue):\n    return check_asis(reply, clue)\n\n# def solve(dataset):\n#     a, b = dataset.split()\n#     return str(int(a) + int(b))        \n    ",
                    "execution_time_limit": 5,
                    "execution_memory_limit": 256,
                    "samples_count": 2,
                    "templates_data": "\n::c\n::header\n#include <stdio.h>\nint module(int x);\n::footer\nint main()\n{\n  int x;\n  scanf(\"%d\", &x);\n  printf(\"%d\n\", module(x));\n  return 0;\n}\n::code\nint module(int x) {\n  // здесь нужно написать код\n}\n\n::c++\n::header\n#include <iostream>\nint module(int x);\n::footer\nint main()\n{\n  int x;\n  std::cin >> x;\n  std::cout << module(x)) << std::endl;\n  return 0;\n}\n::code\nint module(int x) {\n  // здесь нужно написать код\n}",
                    "is_time_limit_scaled": True,
                    "is_memory_limit_scaled": True,
                    "is_run_user_code_allowed": True,
                    "manual_time_limits": [],
                    "manual_memory_limits": [],
                    "test_archive": [],
                    "test_cases": [
                        (
                            "2 3",
                            "5"
                        ),
                        (
                            "-17 -23",
                            "-40"
                        )
                    ]
                },
                "feedback_correct": "",
                "feedback_wrong": ""
            },
            "instruction_type": None,
            "lesson_id": None,
            "position": 2,
            "status": "ready",
            "is_enabled": True,
            "needs_plan": None,
            "instruction": None,
            "lesson": "1950070",
            "score": 10
        }
    }
    assert expected_dict == res