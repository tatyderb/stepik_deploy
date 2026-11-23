"""Генерация Python-проверки SQL-задачи из декларативных тестов."""

import ast


# Это передаётся в Stepik
SQL_CHECKER_TEMPLATE = r'''
from datetime import date, datetime, time
from decimal import Decimal


def _same_value(actual, expected, tolerance):
    if actual is None or expected is None:
        return actual is None and expected is None
    numbers = (int, float, Decimal)
    if (isinstance(actual, numbers) and not isinstance(actual, bool)
            and isinstance(expected, numbers) and not isinstance(expected, bool)):
        left, right = Decimal(str(actual)), Decimal(str(expected))
        return left.is_finite() and right.is_finite() and abs(left - right) <= tolerance
    if isinstance(actual, datetime):
        actual = actual.isoformat(sep=' ')
    elif isinstance(actual, (date, time)):
        actual = actual.isoformat()
    return type(actual) is type(expected) and actual == expected


def _same_rows(actual, expected, ordered, tolerance):
    if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
        return False

    def same_row(left, right):
        return (isinstance(left, (list, tuple)) and len(left) == len(right)
                and all(_same_value(a, b, tolerance) for a, b in zip(left, right)))

    if ordered:
        return all(same_row(a, b) for a, b in zip(actual, expected))

    # Полное паросочетание сохраняет дублмкаты и учитывает пересекающиеся допуски
    edges = [[j for j, row in enumerate(expected) if same_row(value, row)]
             for value in actual]
    matched = {}
    for start in range(len(actual)):
        queue, parent, seen = [start], {}, set()
        free = None
        for left in queue:
            for right in edges[left]:
                if right in seen:
                    continue
                seen.add(right)
                parent[right] = left
                if right not in matched:
                    free = right
                    break
                queue.append(matched[right])
            if free is not None:
                break
        if free is None:
            return False
        previous = {left: right for right, left in matched.items()}
        while free is not None:
            left = parent[free]
            matched[free] = left
            free = previous.get(left)
    return True


def check(query, result):
    for number, test in enumerate(_STEPKIT_SQL_TESTS, 1):
        if test['sql'] is None:
            index = test['result_index']
            if index is None:
                if isinstance(result, list):
                    return False, 'Проверка %s: укажите номер результата в TEST.' % number
                actual = result
            else:
                results = result if isinstance(result, list) else [result]
                if index > len(results):
                    return False, 'Проверка %s: отсутствует результат запроса %s.' % (number, index)
                actual = results[index - 1]
        else:
            try:
                affected = cursor.execute(test['sql'])
                columns = [column[0] for column in cursor.description] if cursor.description else []
                rows = cursor.fetchall() if cursor.description else []
                actual = {'rows': rows, 'columns': columns, 'affected_rows': affected}
            except Exception:
                return False, 'Проверка %s: не удалось выполнить проверочный SQL-запрос.' % number

        expected = test['expected']
        if not isinstance(actual, dict):
            return False, 'Проверка %s: неверный формат результата.' % number
        if 'columns' in expected and actual.get('columns') != expected['columns']:
            return False, 'Проверка %s: не совпадают имена или порядок столбцов.' % number
        if 'affected_rows' in expected and actual.get('affected_rows') != expected['affected_rows']:
            return False, 'Проверка %s: не совпадает число затронутых строк.' % number
        if 'rows' in expected:
            tolerance = Decimal(str(expected.get('tolerance', 0)))
            if not _same_rows(actual.get('rows'), expected['rows'],
                              expected.get('ordered', True), tolerance):
                return False, 'Проверка %s: результат не совпадает с ожидаемым.' % number
    return True
'''


def generate_sql_check(tests: list[dict]) -> str:
    """Создаёт модуль для Stepik,"""
    return '# Проверка SQL, сгенерированная StepKIT.\n_STEPKIT_SQL_TESTS = ' + repr(tests) + '\n' + SQL_CHECKER_TEMPLATE


def extract_sql_tests(code: str) -> list[dict] | None:
    """Восстанавливает TEST только из неизменённого сгенерированного модуля"""
    try:
        tree = ast.parse(code)
        assignment = tree.body[0]
        if not isinstance(assignment, ast.Assign):
            return None
        if len(assignment.targets) != 1 or not isinstance(assignment.targets[0], ast.Name):
            return None
        if assignment.targets[0].id != '_STEPKIT_SQL_TESTS':
            return None
        tests = ast.literal_eval(assignment.value)
        if isinstance(tests, list) and generate_sql_check(tests).strip() == code.strip():
            return tests
    except (SyntaxError, ValueError, TypeError, IndexError):
        pass
    return None
