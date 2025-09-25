from src.step_tasklinline import ParseSchemaStepTaskinline, StepTaskinline


def test_step_inline_simple():
    text="""
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
    res = ParseSchemaStepTaskinline.step_taskinline().parseString(text).as_dict()
    print(f'\nParseSchemaStepTaskinline.step_taskinline: \n{res=}')
    expected_res = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
                    'tests': ['2 3', '5', '-17 -23', '-40']}
    assert res == expected_res

    text2 = """
HEADER
#include <stdio.h>
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
"""
    res = ParseSchemaStepTaskinline.step_taskinline().parseString(text + text2).as_dict()
    print(f'\nParseSchemaStepTaskinline.step_taskinline: \n{res=}')
    expected_res = {'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
           'tests': ['2 3', '5', '-17 -23', '-40'], 'header': '#include <stdio.h>\nint module(int x);',
           'footer': 'int main()\n{\n    int x;\n    scanf("%d", &x);\n    printf("%d\n", module(x));\n    return 0;\n}',
           'code': 'int module(int x) {\n    // здесь нужно написать код\n}', 'config': [{'lang': 'c'}]}

    assert res == expected_res

def test_example_section():
    # все тесты (по умолчанию)
    expected_html = "<details><summary>Тестовые данные</summary>\n\n<h4>Test #1 input</h4>\n<pre>3 2</pre>\n<h4>Test #1 output</h4>\n<pre>-3 2</pre>\n\n\n<h4>Test #2 input</h4>\n<pre>-3 2</pre>\n<h4>Test #2 output</h4>\n<pre>3 2</pre>\n\n\n<h4>Test #3 input</h4>\n<pre>-10 -7</pre>\n<h4>Test #3 output</h4>\n<pre>10 -7</pre>\n\n\n<h4>Test #4 input</h4>\n<pre>10 -7</pre>\n<h4>Test #4 output</h4>\n<pre>-10 -7</pre>\n\n\n<h4>Test #5 input</h4>\n<pre>0 0</pre>\n<h4>Test #5 output</h4>\n<pre>0 0</pre>\n</details>"
    tests = [['3 2', '-3 2'], ['-3 2', '3 2'], ['-10 -7', '10 -7'], ['10 -7', '-10 -7'], ['0 0', '0 0']]
    s = StepTaskinline()
    res = s.test_examples(tests, visible_tests_number=-1)
    print(f'\n{res=}')
    assert res == expected_html

    # # 3 открытых теста
    expected_html = "<details><summary>Тестовые данные</summary>\n\n<h4>Test #1 input</h4>\n<pre>3 2</pre>\n<h4>Test #1 output</h4>\n<pre>-3 2</pre>\n\n\n<h4>Test #2 input</h4>\n<pre>-3 2</pre>\n<h4>Test #2 output</h4>\n<pre>3 2</pre>\n\n\n<h4>Test #3 input</h4>\n<pre>-10 -7</pre>\n<h4>Test #3 output</h4>\n<pre>10 -7</pre>\n<p>Остальные тесты закрыты авторами курса.</p>\n</details>"
    res = s.test_examples(tests, visible_tests_number=3)
    print(f'\n{res=}')
    assert res == expected_html

    # Тестов нет
    expected_html = "<details><summary>Тестовые данные</summary>\nДанные закрыты.</details>"
    res = s.test_examples(tests, visible_tests_number=0)
    print(f'\n{res=}')
    assert res == expected_html

    expected_html = ''
    res = s.test_examples(tests, visible_tests_number=-2)
    print(f'\n{res=}')
    assert res == expected_html
