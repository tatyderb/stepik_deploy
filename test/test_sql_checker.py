"""Проверки сгенерированного модуля """

from datetime import date, datetime
from decimal import Decimal
import json
import sqlite3
from pathlib import Path

import pytest

from src.step_sql import StepSql
from src.lesson import Lesson
from src.export.dump import get_exporter
from src.sql_checker import extract_sql_tests


class SqliteCursor:
    """Адаптер курсора к используемой части интерфейса MySQL"""

    def __init__(self, connection):
        self.cursor = connection.cursor()
        self.description = None
        self.rows = []

    def execute(self, query):
        self.cursor.execute(query)
        self.description = self.cursor.description
        self.rows = self.cursor.fetchall() if self.description else []
        return len(self.rows) if self.description else self.cursor.rowcount

    def fetchall(self):
        return self.rows


@pytest.fixture
def database():
    """Создаёт базу с пользователями и заказами для каждого теста"""
    connection = sqlite3.connect(':memory:')
    connection.executescript('''
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, balance INTEGER);
        INSERT INTO users VALUES (1, 'Анна', 100), (2, 'Борис', 200);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER);
        INSERT INTO orders VALUES (1, 1, 10), (2, 1, 20), (3, 2, 40);
    ''')
    yield SqliteCursor(connection)
    connection.close()


def make_checker(blocks, cursor=None):
    """Компилирует именно код, который StepKIT отправляет в Stepik."""
    step = StepSql()
    step.parse('TEST\n' + '\n'.join(
        target + '\n----\n' + json.dumps(expected, ensure_ascii=False) + '\n===='
        for target, expected in blocks))
    namespace = {'cursor': cursor}
    exec(step.to_dict()['stepSource']['block']['source']['check_code'], namespace)
    return namespace['check'], step


def submit(cursor, query):
    """Формирует результат в формате, описанном документацией Stepik."""
    affected = cursor.execute(query)
    return {'rows': cursor.fetchall(),
            'columns': [col[0] for col in cursor.description] if cursor.description else [],
            'affected_rows': affected}


def test_join_group_by_and_columns(database):
    """Принимает правильную группировку и отклоняет неверные данные и заголовки."""
    query = ('SELECT u.name, SUM(o.amount) AS total FROM users u '
             'JOIN orders o ON u.id=o.user_id GROUP BY u.name ORDER BY u.name')
    check, _ = make_checker([('RESULT', {'columns': ['name', 'total'],
                                        'rows': [['Анна', 30], ['Борис', 40]]})])
    assert check(query, submit(database, query)) is True
    assert check('', {'rows': [['Анна', 10], ['Борис', 40]], 'columns': ['name', 'total']})[0] is False
    assert check('', {'rows': [['Анна', 30], ['Борис', 40]], 'columns': ['name', 'sum']})[0] is False


@pytest.mark.parametrize('query, valid', [
    ("INSERT INTO users VALUES (3, 'Вера', 0)", True),
    ("INSERT INTO users VALUES (3, 'Галина', 0)", False),
    ("DELETE FROM users WHERE id=1", False),
])
def test_insert_and_preserved_rows(database, query, valid):
    """Проверяет состояние базы, включая сохранность исходных записей."""
    check, _ = make_checker([
        ('SELECT id, name FROM users ORDER BY id', [[1, 'Анна'], [2, 'Борис'], [3, 'Вера']]),
        ('SELECT COUNT(*) FROM orders', [[3]]),
    ], database)
    result = submit(database, query)
    verdict = check(query, result)
    assert (verdict is True) is valid


def test_multiple_statements_and_multiple_tables(database):
    """Проверяет результаты UPDATE и DELETE, а затем обе изменённые таблицы."""
    queries = ['UPDATE users SET balance=balance-10 WHERE id=1', 'DELETE FROM orders WHERE id=1']
    results = [submit(database, query) for query in queries]
    check, _ = make_checker([
        ('RESULT 1', {'affected_rows': 1}),
        ('RESULT 2', {'affected_rows': 1}),
        ('SELECT balance FROM users ORDER BY id', [[90], [200]]),
        ('SELECT id FROM orders ORDER BY id', [[2], [3]]),
    ], database)
    assert check(';'.join(queries), results) is True
    assert check('', results[:1])[0] is False
    check, _ = make_checker([('RESULT', [])])
    assert check('', results)[0] is False


def test_create_table_and_window_query(database):
    """Проверяет созданную таблицу и результат оконной функции."""
    submit(database, 'CREATE TABLE totals AS SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id')
    check, _ = make_checker([
        ('SELECT user_id, total, ROW_NUMBER() OVER (ORDER BY total DESC) FROM totals ORDER BY total DESC',
         [[2, 40, 1], [1, 30, 2]])
    ], database)
    assert check('', {}) is True


@pytest.mark.parametrize('actual, expected, valid', [
    ([[2], [1], [1]], {'rows': [[1], [2], [1]], 'ordered': False}, True),
    ([[2], [2], [1]], {'rows': [[1], [2], [1]], 'ordered': False}, False),
    ([[2], [1]], {'rows': [[1], [2]]}, False),
    ([[None], ['']], {'rows': [[None], ['']]}, True),
    ([['NULL']], {'rows': [[None]]}, False),
    ([[Decimal('1.001')]], {'rows': [[1]], 'tolerance': 0.01}, True),
    ([[Decimal('1.02')]], {'rows': [[1]], 'tolerance': 0.01}, False),
    # Жадное сравнение выбирало бы для 0.1 строку 0 и отвергало правильный ответ.
    ([[0.1], [0]], {'rows': [[0], [0.2]], 'ordered': False, 'tolerance': 0.11}, True),
    ([[date(2026, 1, 2), datetime(2026, 1, 2, 3, 4, 5)]],
     {'rows': [['2026-01-02', '2026-01-02 03:04:05']]}, True),
    ([], {'rows': []}, True),
    ([[1]], {'rows': [['1']]}, False),
])
def test_comparison_rules(actual, expected, valid):
    """Проверяет порядок, дубликаты, NULL, точность чисел и даты."""
    check, _ = make_checker([('RESULT', expected)])
    assert (check('', {'rows': actual}) is True) is valid


def test_query_error_is_not_accepted(database):
    """Отсутствующая таблица даёт отрицательный результат без раскрытия эталона."""
    check, _ = make_checker([('SELECT * FROM missing', [])], database)
    assert check('', {}) == (False, 'Проверка 1: не удалось выполнить проверочный SQL-запрос.')


def test_expected_strings_are_not_executed():
    """Кавычки и Python-код внутри ожидаемой строки остаются данными."""
    value = "'); raise RuntimeError('не выполнять') #"
    check, step = make_checker([('RESULT', [[value]])])
    assert check('', {'rows': [[value]]}) is True
    assert extract_sql_tests(step.check_code) == step.tests
    assert extract_sql_tests(step.check_code + '\n# Ручное изменение') is None


@pytest.mark.parametrize('target, expected', [
    ('RESULT 0', []), ('RESULT abc', []), ('', []),
    ('RESULT', {'rows': [1]}), ('RESULT', {'rows': [[1], [1, 2]]}),
    ('RESULT', {'rows': [[1]], 'columns': ['a', 'b']}),
    ('RESULT', {'rows': [], 'ordered': 'false'}),
    ('RESULT', {'rows': [], 'tolerance': -1}),
    ('RESULT', {'rows': [], 'tolerance': float('nan')}),
    ('RESULT', {'rows': [[float('inf')]]}),
    ('RESULT', {'affected_rows': True}), ('RESULT', {}),
    ('RESULT', {'ordered': False}), ('RESULT', {'column': ['a']}),
])
def test_invalid_tests(target, expected, capsys):
    """Неверные декларации отклоняются до отправки на Stepik."""
    with pytest.raises(SystemExit):
        make_checker([(target, expected)])
    assert 'TEST' in capsys.readouterr().err


@pytest.mark.parametrize('body', ['RESULT\n----\n[]', 'RESULT\n----\nне JSON\n====', ''])
def test_invalid_test_blocks(body, capsys):
    """Проверяет обязательные разделители и корректность JSON."""
    with pytest.raises(SystemExit):
        StepSql().parse('TEST\n' + body)
    assert 'TEST' in capsys.readouterr().err


def test_complete_examples_round_trip():
    """Проверяет оба документированных задания через разбор урока и экспорт."""
    example = Path(__file__).resolve().parents[1] / 'examples' / 'step_sql_test.md'
    lesson = Lesson(lesson_id=123)
    lesson.parse_markdown(example.read_text())
    assert len(lesson.steps) == 2
    assert [len(step.tests) for step in lesson.steps] == [1, 4]
    exported = '\n'.join(get_exporter(step.to_dict()['stepSource'], i).export()
                         for i, step in enumerate(lesson.steps, 1))
    imported = Lesson(lesson_id=123)
    imported.parse_markdown('# SQL\nlesson: 0\n\n' + exported)
    assert [step.to_dict() for step in imported.steps] == [step.to_dict() for step in lesson.steps]
