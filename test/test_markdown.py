import pytest
from pyparsing import ParseException
import sys

from src.markdown_parsing import ParseSchema, ParseSchemaStepNumber

@pytest.fixture(scope="module")
def md_file():
    return ['']


@pytest.mark.parametrize("text, number", [
    ('123', '123'),
    ('-123', '-123'),
    ('3.14', '3.14'),
    ('-3.14', '-3.14'),
    ('0.15', '0.15'),
    ('-0.123', '-0.123')
])
def test_number_schema(text, number):
    res = ParseSchema.number().parseString(text)
    print(res)
    # print(f'{res=}, {res.step_type=}, {res.skip=}, {res.header=}')
    assert res.number == number


def test_capture_output(capsys):
    """Пример теста, который проверяет содержимое stdout и stderr"""
    print('hello')
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

    print('good bye!', file=sys.stderr)
    captured = capsys.readouterr()
    assert captured.err == "good bye!\n"

@pytest.mark.parametrize("text, expected_vars", [
    ('lesson = 1234', {'lesson': '1234'}),
    ('lesson = 1234\nlang = c\n', {'lesson': '1234', 'lang': 'c'}),
    ('lesson=1234\n', {'lesson': '1234'}),
    ('lang=c', {'lang': 'c'}),
    ('lang: c', {'lang': 'c'}),
    ('lang = python3.12', {'lang': 'python3.12'}),
])
def test_variables_schema(text, expected_vars):

    vars = ParseSchema.parse_variables(text)
    print(f'{vars=}')
    assert vars == expected_vars

@pytest.mark.parametrize("text, error_message", [
    ("lang = \n", "Expected end of text, found 'lang'"),
    ("lang\n", "Expected end of text, found 'lang'"),
    ("lesson=123\nlang\n", "Expected end of text, found 'lang'"),
])
def test_wrong_var_parsing(text, error_message):
    # vars = ParseSchema.parse_variables(text)
    # print(vars)
    with pytest.raises(ParseException, match=error_message):
        # code that should raise
        ParseSchema.parse_variables(text, test_mode=True)


@pytest.mark.parametrize("text, step_type, skip, header", [
    ('QUIZ its my test', 'QUIZ', '', 'its my test'),
    ('SKIP TASKINLINE  its my test', 'TASKINLINE', 'SKIP', 'its my test'),
    ('NUMBER SKIP its my test', 'NUMBER', 'SKIP', 'its my test'),
    ('only header', '', '', 'only header'),
    ('\n', '', '', ''),
    (' \n', '', '', ''),
])
def test_h2_schema(text, step_type, skip, header):
    res = ParseSchema.step_header().parseString(text)
    # print(text)
    # print(f'{res=}, {res.step_type=}, {res.skip=}, {res.header=}')
    assert res.type == step_type
    assert res.skip == skip
    assert res.header.strip() == header

@pytest.mark.parametrize("text, ok, step_type, skip, header", [
    ('QUIZ its my test', True, 'QUIZ', False, 'its my test'),
    ('SKIP TASKINLINE  its my test', True, 'TASKINLINE', True, 'its my test'),
    ('NUMBER SKIP its my test', True, 'NUMBER', True, 'its my test'),
    ('only header', True, 'TEXT', False, 'only header'),
    ('\n', True, 'TEXT', False, ''),
])
def test_parse_step_header(text, ok, step_type, skip, header):
    res_ok, res_step_type, res_skip, res_header = ParseSchema.parse_step_header(text)
    assert res_ok == ok
    assert res_skip == skip
    assert res_step_type == step_type
    assert res_header == header

# @pytest.mark.parametrize('text, ok, number, accuracy', [
#     ('ANSWER: 123', True, 123, 0),
#     ('ANSWER: -123', True, -123, 0),
#     ('ANSWER: 3.14', True, 3.14, 0),
#     ('ANSWER: -3.14', True, -3.14, 0),
#     ('ANSWER: 123 +-7', True, 123, 7),
#     ('ANSWER: 123 +- 5', True, 123, 5),
#     ('ANSWER: -123 +-1', True, -123, 1),
#     ('ANSWER: 3.14 +-0.1', True, 3.14, 0.1),
#     ('ANSWER: -234.567 +-0.002', True, -234.567, 0.002),
# ])
# def test_parse_step_number_answer(text, ok, number, accuracy):
#     res_ok, res_number, res_accuracy = ParseSchemaStepNumber.parse_answer(text)
#     assert res_ok == ok
#     assert res_number == number
#     assert res_accuracy == accuracy




