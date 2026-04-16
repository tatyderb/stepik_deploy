"""
Тесты для экспорта TASKINLINE шагов (задачи на программирование)
"""

import pytest
from src.export.dump import TaskinlineDump, get_exporter


pytestmark = pytest.mark.step_begin("---1234")


@pytest.fixture
def basic_taskinline_data():
    """Фикстура: простой TASKINLINE шаг с тестами"""
    return {
        "block": {
            "name": "code",
            "text": "<h2>Сумма чисел</h2><p>Даны два целых числа, напечатайте их сумму.</p>",
            "source": {
                "test_cases": [
                    ["2 3", "5"],
                    ["-7 -14", "-21"]
                ],
                "lang": "python3",
                "mode": "stepik",
                "open_tests": 2,
                "checker": "check_asis"
            }
        },
        "cost": 10
    }


@pytest.fixture
def taskinline_without_tests():
    """Фикстура: TASKINLINE шаг без тестов"""
    return {
        "block": {
            "name": "code",
            "text": "<h2>Нет тестов</h2><p>Напишите функцию hello().</p>",
            "source": {
                "test_cases": [],
                "lang": "all"
            }
        },
        "cost": 5
    }


def test_taskinline_basic_export(basic_taskinline_data):
    """Проверка базового экспорта TASKINLINE шага"""
    exporter = TaskinlineDump(basic_taskinline_data, position=1)
    result = exporter.export()

    expected = """---1234 TASKINLINE

## Сумма чисел

Даны два целых числа, напечатайте их сумму.

TEST
2 3
----
5
====
-7 -14
----
-21
====

CONFIG
score: 10
lang: python3
mode: stepik
open_tests: 2
checker: check_asis"""

    assert result.strip() == expected.strip()


def test_taskinline_without_title():
    """Проверка экспорта TASKINLINE шага без заголовка"""
    step_data = {
        "block": {
            "name": "code",
            "text": "<p>Даны два числа, найдите сумму.</p>",
            "source": {
                "test_cases": [["1 2", "3"]],
                "lang": "c"
            }
        },
        "cost": 10
    }
    exporter = TaskinlineDump(step_data, position=3)
    result = exporter.export()

    expected = """---1234 TASKINLINE

Даны два числа, найдите сумму.

TEST
1 2
----
3
====

CONFIG
score: 10
lang: c"""

    assert result.strip() == expected.strip()


def test_taskinline_without_tests(taskinline_without_tests):
    """Проверка экспорта TASKINLINE шага без тестов"""
    exporter = TaskinlineDump(taskinline_without_tests, position=1)
    result = exporter.export()

    expected = """---1234 TASKINLINE

## Нет тестов

Напишите функцию hello().

CONFIG
score: 5
lang: all"""

    assert result.strip() == expected.strip()


def test_taskinline_with_multiple_tests():
    """Проверка экспорта с множеством тестов"""
    step_data = {
        "block": {
            "name": "code",
            "text": "<h2>Сортировка</h2><p>Отсортируйте массив.</p>",
            "source": {
                "test_cases": [
                    ["3 1 2", "1 2 3"],
                    ["5 4 3 2 1", "1 2 3 4 5"],
                    ["1", "1"],
                    ["", ""]
                ],
                "lang": "python3",
                "mode": "custom",
                "open_tests": 2,
                "checker": "check_int_seq"
            }
        },
        "cost": 15
    }
    exporter = TaskinlineDump(step_data, position=1)
    result = exporter.export()

    expected = """---1234 TASKINLINE

## Сортировка

Отсортируйте массив.

TEST
3 1 2
----
1 2 3
====
5 4 3 2 1
----
1 2 3 4 5
====
1
----
1
====

----

====

CONFIG
score: 15
lang: python3
mode: custom
open_tests: 2
checker: check_int_seq"""

    assert result.strip() == expected.strip()


def test_taskinline_config_filtering():
    """Проверка, что в CONFIG попадают только разрешенные параметры"""
    step_data = {
        "block": {
            "name": "code",
            "text": "<p>Тест фильтрации.</p>",
            "source": {
                "test_cases": [["1", "1"]],
                "lang": "python3",
                "mode": "stepik",
                "open_tests": 1,
                "checker": "check_asis",
                "extra_param": "should_be_filtered",
                "another_param": 123
            }
        },
        "cost": 10
    }
    exporter = TaskinlineDump(step_data, position=1)
    result = exporter.export()

    expected = """---1234 TASKINLINE

Тест фильтрации.

TEST
1
----
1
====

CONFIG
score: 10
lang: python3
mode: stepik
open_tests: 1
checker: check_asis"""

    assert result.strip() == expected.strip()


def test_get_exporter_returns_taskinline_dump():
    """Проверка, что get_exporter возвращает TaskinlineDump для code шагов"""
    step_data = {"block": {"name": "code", "text": "<p>Тест</p>"}}
    exporter = get_exporter(step_data, 1)
    assert isinstance(exporter, TaskinlineDump)