"""
Тесты для экспорта STRING шагов с использованием pytest.
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

from src.export.dump import StringDump


class TestStringDump:
    """Тесты для экспорта STRING шагов"""

    @pytest.fixture
    def simple_step_data(self) -> Dict[str, Any]:
        """Фикстура: простой строковый шаг"""
        return {
            "id": 8491277,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Простой случай</h2>\n<p>Как называется шахматная фигура, которая ходит по вертикали и горизонтали?</p>",
                "source": {
                    "pattern": "ладья",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": "# def check(reply):\n#     return reply == \"Hello\""
                }
            }
        }

    @pytest.fixture
    def case_sensitive_step_data(self) -> Dict[str, Any]:
        """Фикстура: шаг с учётом регистра"""
        return {
            "id": 8491277,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Демонстрация опции CONFIG</h2>\n<p>Назовите столицу России</p>",
                "source": {
                    "pattern": "Москва",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": True,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def regex_step_data(self) -> Dict[str, Any]:
        """Фикстура: шаг с регулярным выражением"""
        return {
            "id": 8496387,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Регулярные выражения</h2>\n<p>Напишите север или юг</p>",
                "source": {
                    "pattern": "север|юг",
                    "use_re": True,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def multiline_step_data(self) -> Dict[str, Any]:
        """Фикстура: многострочный ответ"""
        return {
            "id": 8491278,
            "cost": 5,
            "block": {
                "name": "string",
                "text": "<h2>Многострочные ответы</h2>\n<p>Напишите три строки стихотворения</p>",
                "source": {
                    "pattern": "Открой сомкнуты негой взоры\nНавстречу северной Авроры,\nЗвездою севера явись!",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def no_title_step_data(self) -> Dict[str, Any]:
        """Фикстура: шаг без заголовка"""
        return {
            "id": 8491279,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<p>Первый месяц года?</p>",
                "source": {
                    "pattern": "январь",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def file_only_step_data(self) -> Dict[str, Any]:
        """Фикстура: шаг с загрузкой только файла"""
        return {
            "id": 8491281,
            "cost": 3,
            "block": {
                "name": "string",
                "text": "<h2>Загрузка файла</h2>\n<p>Загрузите файл с решением</p>",
                "source": {
                    "pattern": "solution.txt",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": True,
                    "is_file_disabled": False,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def substring_step_data(self) -> Dict[str, Any]:
        """Фикстура: шаг с поиском подстроки"""
        return {
            "id": 8491282,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Поиск подстроки</h2>\n<p>В каком городе находится Кремль?</p>",
                "source": {
                    "pattern": "Москва",
                    "use_re": False,
                    "match_substring": True,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    @pytest.fixture
    def multiple_answers_step_data(self) -> Dict[str, Any]:
        """Фикстура: несколько ответов, объединённых в регулярное выражение"""
        return {
            "id": 8491283,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Множественные ответы</h2>\n<p>Как называется величина det(A)?</p>",
                "source": {
                    "pattern": "детерминант|определитель",
                    "use_re": True,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

    def test_simple_string(self, simple_step_data):
        """Тест: простой строковый шаг без дополнительных опций"""
        exporter = StringDump(simple_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Простой случай

Как называется шахматная фигура, которая ходит по вертикали и горизонтали?

ANSWER: ладья

CONFIG
score: 1
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_case_sensitive(self, case_sensitive_step_data):
        """Тест: шаг с учётом регистра"""
        exporter = StringDump(case_sensitive_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Демонстрация опции CONFIG

Назовите столицу России

ANSWER: Москва

CONFIG
score: 1
use_re: False
case_sensitive: True"""

        assert result.strip() == expected.strip()

    def test_regular_expression(self, regex_step_data):
        """Тест: шаг с регулярным выражением"""
        exporter = StringDump(regex_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Регулярные выражения

Напишите север или юг

ANSWER: север|юг

CONFIG
score: 1
use_re: True
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_multiline_answer(self, multiline_step_data):
        """Тест: многострочный ответ"""
        exporter = StringDump(multiline_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Многострочные ответы

Напишите три строки стихотворения

ANSWER: Открой сомкнуты негой взоры
Навстречу северной Авроры,
Звездою севера явись!

CONFIG
score: 5
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_no_title(self, no_title_step_data):
        """Тест: шаг без заголовка"""
        exporter = StringDump(no_title_step_data, position=7)
        result = exporter.export()

        expected = """## STRING Шаг 7

Первый месяц года?

ANSWER: январь

CONFIG
score: 1
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_file_only(self, file_only_step_data):
        """Тест: шаг с загрузкой только файла"""
        exporter = StringDump(file_only_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Загрузка файла

Загрузите файл с решением

ANSWER: solution.txt

CONFIG
score: 3
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_match_substring(self, substring_step_data):
        """Тест: шаг с поиском подстроки"""
        exporter = StringDump(substring_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Поиск подстроки

В каком городе находится Кремль?

ANSWER: Москва

CONFIG
score: 1
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_multiple_answers_as_regex(self, multiple_answers_step_data):
        """Тест: несколько ответов, объединённых в регулярное выражение"""
        exporter = StringDump(multiple_answers_step_data, position=1)
        result = exporter.export()

        expected = """## STRING Множественные ответы

Как называется величина det(A)?

ANSWER: детерминант|определитель

CONFIG
score: 1
use_re: True
case_sensitive: False"""

        assert result.strip() == expected.strip()

    def test_skip_unnecessary_config_params(self):
        """Тест: проверка, что в CONFIG попадают только разрешенные параметры"""
        step_data = {
            "id": 8491284,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Проверка конфига</h2>\n<p>Тестовый шаг</p>",
                "source": {
                    "pattern": "test",
                    "options": {"some": "option"},
                    "sample_size": 1,
                    "code": "# some code",
                    "use_re": False,
                    "case_sensitive": False,
                    "custom_param": "value"
                }
            }
        }

        exporter = StringDump(step_data, position=1)
        result = exporter.export()

        expected = """## STRING Проверка конфига

Тестовый шаг

ANSWER: test

CONFIG
score: 1
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()
        # Проверяем, что лишние параметры не попали
        assert "options" not in result
        assert "sample_size" not in result
        assert "code" not in result
        assert "custom_param" not in result

    def test_empty_pattern(self):
        """Тест: шаг с пустым pattern"""
        step_data = {
            "id": 8491285,
            "cost": 1,
            "block": {
                "name": "string",
                "text": "<h2>Пустой ответ</h2>\n<p>Введите ответ</p>",
                "source": {
                    "pattern": "",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "is_text_disabled": False,
                    "is_file_disabled": True,
                    "code": ""
                }
            }
        }

        exporter = StringDump(step_data, position=1)
        result = exporter.export()

        expected = """## STRING Пустой ответ

Введите ответ

CONFIG
score: 1
use_re: False
case_sensitive: False"""

        assert result.strip() == expected.strip()
        assert "ANSWER:" not in result

    def test_all_config_options(self):
        """Тест: шаг со всеми возможными опциями"""
        step_data = {
            "id": 8491286,
            "cost": 10,
            "block": {
                "name": "string",
                "text": "<h2>Все опции</h2>\n<p>Тест со всеми настройками</p>",
                "source": {
                    "pattern": "test_pattern",
                    "use_re": True,
                    "match_substring": True,
                    "case_sensitive": True,
                    "is_text_disabled": True,
                    "is_file_disabled": False,
                    "code": "# custom code",
                    "extra_param": "extra_value"
                }
            }
        }

        exporter = StringDump(step_data, position=1)
        result = exporter.export()

        expected = """## STRING Все опции

Тест со всеми настройками

ANSWER: test_pattern

CONFIG
score: 10
use_re: True
case_sensitive: True
"""

        assert result.strip() == expected.strip()
        assert "match_substring" not in result
        assert "is_text_disabled" not in result
        assert "is_file_disabled" not in result
        assert "code" not in result
        assert "extra_param" not in result