"""Тесты разбора SQL-шагов, формирования JSON и обработки ошибок."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.lesson import Lesson
from src.step import Step
from src.step_sql import StepSql


EXAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'step_sql.md'


def example_step():
    """Создаёт SQL-шаг из Markdown-примера."""
    lesson = Lesson(lesson_id=123)
    lesson.parse_markdown(EXAMPLE.read_text())
    return lesson.steps[0]


def test_example_payload_and_transport():
    """Проверяет поля JSON и вызовы загрузки через заглушку сессии."""
    step = example_step()
    assert isinstance(step, StepSql)
    body = step.body(123, 2)
    source = body['stepSource']['block']['source']
    assert body['stepSource']['block']['name'] == 'sql'
    assert body['stepSource']['cost'] == 1
    assert body['stepSource']['lesson'] == 123
    assert body['stepSource']['position'] == 2
    assert source['is_run_user_code_allowed'] is True
    assert source['is_multiple_statements_allowed'] is False
    assert source['solve_sql'] == "INSERT INTO users (name)\nVALUES ('Fluttershy');"
    original = EXAMPLE.read_text().split('\nCHECK\n')[1].split('\nCONFIG\n')[0].strip('\n')
    assert source['check_code'] == original
    assert 'CREATE TABLE users' in source['init_sql']
    assert 'def check' not in body['stepSource']['block']['text']
    session = Mock()
    session.create_object.return_value = 456
    assert step.create(session, 123, 2) == 456
    session.create_object.assert_called_once_with('step-sources', body)
    step.update(session, 123, 456, 2)
    session.update_object.assert_called_once_with('step-sources', 456, body)


def test_fences_order_indentation_and_no_execution():
    """Проверяет секции внутри блоков кода, отступы и отсутствие выполнения CHECK."""
    checker = 'raise RuntimeError("Код не должен выполняться")\n\ndef check(query, result):\n    s = """\nCONFIG\n"""\n    return True'
    step = Step.create_by_type('SQL')
    step.parse('Условие\n```sql\nCHECK\n```\nCHECK\n```python\n' + checker +
               '\n```\nCONFIG\nscore=0\nallow_any_query=false\nallow_multiple_queries=true\n'
               'SOLUTION\nSELECT 1;\nINIT\n')
    assert step.check_code == checker
    assert step.config == {'score': 0, 'allow_any_query': False, 'allow_multiple_queries': True}
    assert step.init_sql == ''
    assert step.to_dict()['stepSource']['block']['source']['is_multiple_statements_allowed'] is True


def test_defaults_and_independent_instances():
    """Проверяет значения по умолчанию и независимость возвращаемых данных."""
    step = StepSql()
    step.parse('CHECK\ndef check(query, result):\n    return True')
    source = step.to_dict()['stepSource']['block']['source']
    assert source['init_sql'] == source['solve_sql'] == ''
    assert source['is_run_user_code_allowed'] is True
    assert source['is_multiple_statements_allowed'] is False
    source['check_code'] = 'изменено'
    assert step.to_dict()['stepSource']['block']['source']['check_code'] != 'изменено'


def test_tabs_line_endings_and_russian_config():
    """Проверяет сохранение табуляции, CRLF и разбор русских булевых значений."""
    checker = 'def check(query, result):\r\n\treturn True'
    step = StepSql()
    step.parse('CHECK\r\n' + checker +
               '\r\nCONFIG\r\nallow_any_query: нет\r\nallow_multiple_queries: да\r\n')
    assert step.check_code == checker
    assert step.config == {'allow_any_query': False, 'allow_multiple_queries': True}


def test_default_body_is_not_modified():
    """Проверяет неизменность общего шаблона после формирования тела запроса."""
    from copy import deepcopy

    template = deepcopy(StepSql.DEFAULT_BODY)
    step = example_step()
    body = step.body(123, 2)
    body['stepSource']['block']['source']['init_sql'] = 'изменено'
    assert StepSql.DEFAULT_BODY == template
    assert step.to_dict()['stepSource']['block']['source']['init_sql'] == step.init_sql


@pytest.mark.parametrize('text, message', [
    ('INIT\nSELECT 1;', 'CHECK'),
    ('CHECK\n', 'CHECK'),
    ('CHECK\ndef check(:', 'Python'),
    ('CHECK\ndef other():\n    pass', 'check'),
    ('CHECK\ndef check(q, r):\n    pass\nCHECK\n', 'повторно'),
    ('CHECK\ndef check(q, r):\n    pass\nTEST\nSELECT 1;', 'TEST'),
    ('CHECK\n```python\ndef check(q, r):\n    pass', 'незакрытый'),
])
def test_invalid_sections(text, message, capsys):
    """Проверяет сообщение об ошибке секции и код завершения."""
    with pytest.raises(SystemExit) as exc:
        StepSql().parse(text)
    assert exc.value.code == 1
    assert message in capsys.readouterr().err


@pytest.mark.parametrize('config', ['score: -1', 'score: 1.5', 'allow_any_query: truejunk',
                                   'unknown: true', 'score: 1\nscore: 2', 'score 2'])
def test_invalid_config(config, capsys):
    """Проверяет отклонение неверных и повторных настроек."""
    with pytest.raises(SystemExit) as exc:
        StepSql().parse('CHECK\ndef check(q, r):\n    return True\nCONFIG\n' + config)
    assert exc.value.code == 1
    assert 'CONFIG' in capsys.readouterr().err
