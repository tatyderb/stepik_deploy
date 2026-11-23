"""Тесты экспорта SQL-шагов в Markdown."""

from pathlib import Path

import pytest

from src.export.dump import get_exporter
from src.lesson import Lesson
from src.step_sql import StepSql


@pytest.fixture
def sql_step():
    """Создаёт SQL-шаг для проверки экспорта из примера задания."""
    example = Path(__file__).resolve().parents[1] / 'examples' / 'step_sql.md'
    lesson = Lesson(lesson_id=123)
    lesson.parse_markdown(example.read_text())
    return lesson.steps[0]


@pytest.mark.parametrize('marker', ['##', '---1234'])
def test_sql_dump_round_trip(marker, monkeypatch, sql_step):
    """Проверяет экспорт и повторный импорт с двумя разделителями шагов."""
    from src.settings import settings
    step = sql_step
    monkeypatch.setattr(settings, 'STEP_BEGIN', marker)
    payload = step.to_dict()['stepSource']
    exported = get_exporter(payload, 1).export()
    lesson = Lesson(lesson_id=123)
    lesson.parse_markdown('# SQL\nlesson: 0\n\n' + exported)
    assert lesson.steps[0].to_dict()['stepSource']['block']['source'] == payload['block']['source']
    assert lesson.steps[0].to_dict()['stepSource']['cost'] == payload['cost']


def test_sql_dump_requires_author_source():
    """Проверяет ошибку при отсутствии авторского кода проверки."""
    with pytest.raises(ValueError, match='авторский доступ'):
        get_exporter({'block': {'name': 'sql', 'text': 'Условие'}}, 1).export()


@pytest.mark.parametrize('modified', [False, True])
def test_generated_check_round_trip(modified):
    """Восстанавливает TEST, но сохраняет вручную изменённый модуль как CHECK."""
    step = StepSql()
    step.parse('TEST\nRESULT 1\n----\n{"rows": [[1]], "ordered": false}\n====\n'
               'SELECT COUNT(*) FROM users\n----\n[[3]]\n====')
    if modified:
        step.check_code += '\n# Дополнительный комментарий автора\n'
    payload = step.to_dict()['stepSource']
    exported = get_exporter(payload, 1).export()
    assert ('\nTEST\n' in exported) is not modified
    assert ('\nCHECK\n' in exported) is modified
    lesson = Lesson(lesson_id=123)
    lesson.parse_markdown('# SQL\nlesson: 0\n\n' + exported)
    assert lesson.steps[0].check_code.strip() == step.check_code.strip()
    assert lesson.steps[0].tests == ([] if modified else step.tests)
