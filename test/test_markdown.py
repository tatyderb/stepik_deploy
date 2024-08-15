import pytest
from pyparsing import ParseException
import sys

from src.markdown_parsing import ParseSchema

@pytest.fixture(scope="module")
def md_file():
    return ['']


@pytest.mark.parametrize("text", [
    '# Заголовок',
    '# Длинный заголовок',
    '# ',
    '#\n'
])
def test_h1(text):
    title = ParseSchema.parse_h1(text)
    assert title == text[2:]


def test_wrong_h1():
    s = '#Слитный Заголовок'
    with pytest.raises(ParseException):
        ParseSchema.h1().parseString(s)

    # ParseSchema.parse_h1(s)


def test_capture_output(capsys):
    """Пример теста, который проверяет содержимое stdout и stderr"""
    print('hello')
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

    print('good bye!', file=sys.stderr)
    captured = capsys.readouterr()
    assert captured.err == "good bye!\n"

@pytest.mark.parametrize("text, var, val", [
    ('lesson = 1234', 'lesson', '1234'),
    ('lesson=1234', 'lesson', '1234'),
    ('lang=c', 'lang', 'c'),
    ('lang = python3.12', 'lang', 'python3.12'),
])
def test_variable_schema(text, var, val):
    res = ParseSchema.variable_value().parseString(text)
    # print(res.variable, res.value)
    assert res.variable == var
    assert res.value.strip() == val

@pytest.mark.parametrize("text, ok, var, val", [
    ('lesson = 1234', True, 'lesson', '1234'),
    ('lesson=1234', True, 'lesson', '1234'),
    ('lang=c', True, 'lang', 'c'),
    ('lang = python3.12', True, 'lang', 'python3.12'),
    ('lang=', True, 'lang', ''),
    ('lang', False, None, None),
    ('qqq=zzz', False, None, None),
])
def test_parse_variable_value(text, ok, var, val):
    res_ok, res_var, res_val = ParseSchema.parse_variable_value(text)
    assert res_ok == ok
    assert res_var == var
    assert res_val == val

@pytest.mark.parametrize("text, step_type, skip, header", [
    ('## QUIZ its my test', 'QUIZ', '', 'its my test'),
    ('## SKIP TASKINLINE  its my test', 'TASKINLINE', 'SKIP', 'its my test'),
    ('## NUMBER SKIP its my test', 'NUMBER', 'SKIP', 'its my test'),
    ('## only header', '', '', 'only header'),
    ('##\n', '', '', ''),
])
def test_h2_schema(text, step_type, skip, header):
    res = ParseSchema.step_header().parseString(text)
    # print(text)
    # print(f'{res=}, {res.step_type=}, {res.skip=}, {res.header=}')
    assert res.type == step_type
    assert res.skip == skip
    assert res.header.strip() == header

@pytest.mark.parametrize("text, ok, step_type, skip, header", [
    ('## QUIZ its my test', True, 'QUIZ', False, 'its my test'),
    ('## SKIP TASKINLINE  its my test', True, 'TASKINLINE', True, 'its my test'),
    ('## NUMBER SKIP its my test', True, 'NUMBER', True, 'its my test'),
    ('## only header', True, 'TEXT', False, 'only header'),
    ('##\n', True, 'TEXT', False, ''),
    ('###', False, None, False, ''),
    ('# ошибочка', False, None, False, ''),
    ('   ## комментарий', False, None, False, ''),
])
def test_parse_step_header(text, ok, step_type, skip, header):
    res_ok, res_skip, res_step_type, res_header = ParseSchema.parse_step_header(text)
    assert res_ok == ok
    assert res_skip == skip
    assert res_step_type == step_type
    assert res_header == header


