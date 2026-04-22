"""
Тесты для экспорта TASKINLINE шагов.
"""

import pytest
from src.export.dump import TaskinlineDump


pytestmark = pytest.mark.step_begin("---1234")


class TestTaskinlineDump:
    """Тесты для экспорта TASKINLINE шагов"""

    def test_simple_task(self):
        """Простая задача"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Сумма</h2><p>Условие</p>",
                "source": {
                    "test_cases": [["2 3", "5"]],
                    "templates_data": "",
                    "code": ""
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Сумма

Условие

TEST
2 3
----
5
====

CONFIG
score: 10"""

        assert result.strip() == expected.strip()

    def test_task_with_header_code_footer(self):
        """Задача с HEADER, CODE, FOOTER"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Модуль</h2>",
                "source": {
                    "test_cases": [["-5", "5"]],
                    "templates_data": "::c\n::header\nHEADER_TEXT\n::footer\nFOOTER_TEXT\n::code\nCODE_TEXT",
                    "code": ""
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Модуль

TEST
-5
----
5
====

HEADER
HEADER_TEXT

FOOTER
FOOTER_TEXT

CODE
CODE_TEXT

CONFIG
score: 10"""

        assert result.strip() == expected.strip()

    def test_multilang_template(self):
        """Многоязычная задача: выводится TEMPLATE"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Модуль</h2>",
                "source": {
                    "test_cases": [["-5", "5"]],
                    "templates_data": "::c\n::header\nHEADER_C\n::footer\nFOOTER_C\n::code\nCODE_C\n\n::c++\n::header\nHEADER_CPP\n::footer\nFOOTER_CPP\n::code\nCODE_CPP",
                    "code": ""
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Модуль

TEST
-5
----
5
====

TEMPLATE
::c
::header
HEADER_C
::footer
FOOTER_C
::code
CODE_C

::c++
::header
HEADER_CPP
::footer
FOOTER_CPP
::code
CODE_CPP

CONFIG
score: 10"""

        assert result.strip() == expected.strip()

    def test_custom_mode_extracts_tests_from_code(self):
        """mode=custom: тесты извлекаются из my_tests в коде"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Custom</h2>",
                "source": {
                    "test_cases": [],
                    "templates_data": "",
                    "code": "\n\ndef check_int_seq(reply, clue):\n    return True\n\nmy_tests = [('2 3', '5'), ('-7 10', '3'), ('-2 -3', '-5'), ('7 -10', '-3')]\nmy_encoded_tests = ['1 1\\n2 3----\\n5', '2 1\\n-7 10----\\n3', '3 0\\n-2 -3----\\n-5', '4 0\\n7 -10----\\n-3']\n\ndef generate():\n    return [(t[0], ent) for t, ent in zip(my_tests, my_encoded_tests)]\n\ndef check(reply, clue):\n    return True"
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Custom

TEST
2 3
----
5
====
-7 10
----
3
====
-2 -3
----
-5
====
7 -10
----
-3
====

CONFIG
score: 10"""

        assert result.strip() == expected.strip()