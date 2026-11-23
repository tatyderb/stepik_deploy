"""Разбор шага SQL с авторской проверкой CHECK или генерацией проверки из TEST"""

import ast
import json
import math
from copy import deepcopy

import pyparsing as pp

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.sql_checker import generate_sql_check
from src.utils import markdown_to_html


class StepSql(Step):
    DEFAULT_SCORE = 1
    # Поля и значения по умолчанию из SQL редактора Stepik
    SOURCE_FLAGS = {
        'allow_any_query': ('is_run_user_code_allowed', True),
        'allow_multiple_queries': ('is_multiple_statements_allowed', False),
    }

    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'name': 'sql',
                'text': '',
                'video': None,
                'options': None,
                'source': {
                    'init_sql': '',
                    'solve_sql': '',
                    'check_code': '',
                    'is_run_user_code_allowed': True,
                    'is_multiple_statements_allowed': False,
                },
            },
            'lesson': None,
            'position': None,
            'cost': DEFAULT_SCORE,
        },
    }

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)
        self.init_sql = ''
        self.solve_sql = ''
        self.check_code = ''
        self.tests = []

    def parse(self, text: str):
        """Разбирает условие, SQL-код, проверяющий модулб и настройки шага"""
        res = ParseSchemaStepSql.parse_step_sql(text)
        self.text = self.h2() + res['text']
        self.init_sql = res.get('init', '')
        self.solve_sql = res.get('solution', '')
        self.tests = res.get('tests', [])
        self.check_code = generate_sql_check(self.tests) if self.tests else res['check']
        self.config = res.get('config', {})

    def to_dict(self) -> dict:
        """Формирует тело запроса к Stepik из копии шаблона"""
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        source = d['stepSource']['block']['source']
        source['init_sql'] = self.init_sql
        source['solve_sql'] = self.solve_sql
        source['check_code'] = self.check_code
        for option, (field, default) in self.SOURCE_FLAGS.items():
            source[field] = self.config.get(option, default)
        d['stepSource']['cost'] = self.config.get('score', self.DEFAULT_SCORE)
        return d


class ParseSchemaStepSql(ParseSchema):
    SECTION_NAMES = ('INIT', 'SOLUTION', 'CHECK', 'CONFIG', 'TEST')

    @classmethod
    def step_sql(cls) -> pp.ParserElement:
        """Схема: условие и секции INIT, SOLUTION, CHECK/TEST, CONFIG в любом порядке.

        Секции распознаются только с начала строки вне блоков кода.
        Пробелы и табуляция сохраняются.
        """
        names = '|'.join(cls.SECTION_NAMES)
        title = pp.Regex(r'(?m)^(?:' + names + r')[ \t]*(?:\r?\n|$)')
        title.set_parse_action(lambda t: t[0].strip().lower())
        boundary = title | pp.StringEnd()
        content = pp.SkipTo(boundary, ignore=cls.quoted)
        statement = content.copy()('text')
        section = pp.Group(title('name') + content.copy()('body'))
        schema = statement + pp.ZeroOrMore(section)('sections')
        return schema.leave_whitespace().parse_with_tabs()

    @staticmethod
    def unwrap_code(text: str) -> str:
        """Снимает внешние тройные кавычки markdown, сохраняя отступы кода"""
        lines = text.splitlines(keepends=True)
        if lines and lines[0].startswith('```') and lines[-1].strip() == '```':
            return ''.join(lines[1:-1]).strip('\r\n')
        return text

    @staticmethod
    def validate_check(code: str):
        """Проверяет синтаксис и наличие функции check, не выполняя модуль"""
        if not code.strip():
            raise ValueError('SQL: необходима непустая секция CHECK с def check(query, result).')
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            raise ValueError(f'Ошибка Python в строке {exc.lineno}: {exc.msg}') from exc
        if not any(isinstance(node, ast.FunctionDef) and node.name == 'check'
                   for node in tree.body):
            raise ValueError('Нужна функция def check(query, result)')

    @classmethod
    def tests(cls) -> pp.ParserElement:
        """Схема TEST: SQL или RESULT, разделитель ----, JSON и заверщение ===="""
        separator = pp.Regex(r'(?m)^-{4,}[ \t]*(?:\r?\n|$)')
        end = pp.Regex(r'(?m)^={4,}[ \t]*(?:\r?\n|$)')
        test = pp.Group(
            pp.SkipTo(separator, ignore=cls.quoted)('query') + pp.Suppress(separator) +
            pp.SkipTo(end, ignore=cls.quoted)('expected') + pp.Suppress(end))
        return pp.OneOrMore(test).leave_whitespace().parse_with_tabs()

    @staticmethod
    def validate_expected(expected):
        """Проверяет JSON результата и параметры сравнения одного теста"""
        if isinstance(expected, list):
            expected = {'rows': expected}
        fields = {'rows', 'columns', 'affected_rows', 'ordered', 'tolerance'}
        if not isinstance(expected, dict) or set(expected) - fields:
            raise ValueError('SQL TEST: ожидается массив строк или объект rows/columns/affected_rows/ordered/tolerance')
        if not set(expected) & {'rows', 'columns', 'affected_rows'}:
            raise ValueError('SQL TEST: задайте rows, columns или affected_rows')
        if ('ordered' in expected or 'tolerance' in expected) and 'rows' not in expected:
            raise ValueError('SQL TEST: ordered и tolerance применяются только к rows')
        if 'ordered' in expected and type(expected['ordered']) is not bool:
            raise ValueError('SQL TEST: ordered должен быть true или false')
        tolerance = expected.get('tolerance', 0)
        if type(tolerance) not in (int, float) or not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError('SQL TEST: tolerance должен быть конечным числом >= 0')
        if 'affected_rows' in expected:
            count = expected['affected_rows']
            if type(count) is not int or count < 0:
                raise ValueError('SQL TEST: affected_rows должен быть целым числом >= 0')
        if 'columns' in expected:
            columns = expected['columns']
            if not isinstance(columns, list) or not all(isinstance(value, str) for value in columns):
                raise ValueError('SQL TEST: columns должен быть массивом имён столбцов')
        if 'rows' in expected:
            rows = expected['rows']
            if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
                raise ValueError('SQL TEST: rows должен быть массивом строк-массивов')
            widths = {len(row) for row in rows}
            if len(widths) > 1 or ('columns' in expected and widths and widths != {len(expected['columns'])}):
                raise ValueError('SQL TEST: число ячеек должно совпадать во всех строках и с columns')
            for row in rows:
                for value in row:
                    if value is not None and type(value) not in (str, int, float, bool):
                        raise ValueError('SQL TEST: ячейки должны содержать простые JSON-значения')
                    if isinstance(value, float) and not math.isfinite(value):
                        raise ValueError('SQL TEST: нечисловые и бесконечные значения не поддерживаются')
        return expected

    @classmethod
    def parse_tests(cls, text: str) -> list[dict]:
        """Разбирает тесты без выполнения SQL или кода из ожидаемых данных"""
        tests = []
        try:
            parsed = cls.tests().parse_string(text.strip(), parse_all=True)
        except pp.ParseException as exc:
            raise ValueError('SQL TEST: каждый тест должен содержать ---- и завершаться ====') from exc
        for test in parsed:
            query = cls.unwrap_code(test['query'].strip('\r\n')).strip()
            if not query:
                raise ValueError('SQL TEST: укажите SQL-запрос или RESULT')
            target = pp.Keyword('RESULT') + pp.Optional(pp.Word(pp.nums)('index'))
            index = None
            if query.startswith('RESULT'):
                try:
                    res = target.parse_string(query, parse_all=True)
                except pp.ParseException as exc:
                    raise ValueError('SQL TEST: используйте RESULT или RESULT N, где N начинается с 1') from exc
                index = int(res['index']) if 'index' in res else None
                if index is not None and index < 1:
                    raise ValueError('SQL TEST: номер результата начинается с 1')
                query = None
            try:
                expected = json.loads(cls.unwrap_code(test['expected'].strip('\r\n')))
            except (ValueError, TypeError) as exc:
                raise ValueError('SQL TEST: ожидаемый результат должен быть корректным JSON') from exc
            tests.append({'sql': query, 'result_index': index,
                          'expected': cls.validate_expected(expected)})
        return tests

    @classmethod
    def parse_config(cls, text: str) -> dict:
        """Разбирает CONFIG и проверяет допустимые опции и значения"""
        config = {}
        assignment = (pp.Word(pp.alphanums + '_')('key') +
                      pp.Suppress(pp.one_of(': =')) + pp.Regex(r'\S+')('value'))
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                res = assignment.parse_string(line, parse_all=True)
            except pp.ParseException as exc:
                raise ValueError(f'SQL CONFIG: неверная строка {line!r}.') from exc
            key, value = res['key'], res['value']
            if key in config:
                raise ValueError(f'SQL CONFIG: повторная опция {key}.')
            if key == 'score':
                if not value.isascii() or not value.isdecimal():
                    raise ValueError('SQL CONFIG: score должен быть целым неотрицательным числом')
                config[key] = int(value)
            elif key in StepSql.SOURCE_FLAGS:
                # Общий to_boolean допускает совпадение префикса.
                if value.lower() not in {'true', 'false', '1', '0', 'yes', 'no', 'on', 'off', 'y', 'n', 'enable', 'disable', 'да', 'нет', 'вкл', 'выкл', '+', '-'}:
                    raise ValueError(f'SQL CONFIG: неверное булево значение {value!r}.')
                config[key] = cls.to_boolean(value)
            else:
                raise ValueError(f'SQL CONFIG: неизвестная опция {key}')
        return config

    @classmethod
    def parse_step_sql(cls, text: str) -> dict:
        """Разбирает шаг и сообщает об ошибках общим обработчиком проекта"""
        try:
            res = cls.step_sql().parse_string(text, parse_all=True)
            result = {'text': res['text'].strip('\r\n')}
            for section in res['sections']:
                name = section['name']
                if name in result:
                    raise ValueError(f'SQL: секция {name.upper()} указана повторно')
                result[name] = section['body'].strip('\r\n')
            for value in result.values():
                if value.count('```') % 2:
                    raise ValueError('SQL: незакрытый блок кода ```.')
            for name in ('init', 'solution', 'check'):
                if name in result:
                    result[name] = cls.unwrap_code(result[name])
            if 'test' in result and 'check' in result:
                raise ValueError('SQL: укажите только одну секцию: CHECK или TEST')
            if 'test' in result:
                result['tests'] = cls.parse_tests(result.pop('test'))
            else:
                cls.validate_check(result.get('check', ''))
            result['config'] = cls.parse_config(result.get('config', ''))
            return result
        except pp.ParseException as exc:
            parse_error(exc.lineno, exc.line, exc.msg)
        except ValueError as exc:
            parse_error(error_msg=str(exc))
