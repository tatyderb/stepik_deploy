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

    def test_custom_mode_stepik(self):
        """mode=stepik: тесты извлекаются из test_cases"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Stepik mode</h2>",
                "source": {
                    "test_cases": [
                        ["2 3", "5"],
                        ["-7 10", "3"],
                        ["-2 -3", "-5"],
                        ["7 -10", "-3"]
                    ],
                    "templates_data": "",
                    "code": ""
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Stepik mode

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