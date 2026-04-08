"""Тесты для проверки работы с разными разделителями шагов."""
import json
from pathlib import Path
import pytest
import sys

from src.markdown_parsing import ParseSchema
from src.settings import settings


# Добавляем корневую директорию проекта в путь импорта
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Тесты со старой версией начала шага смотри в test_lesson.py


@pytest.mark.step_begin(">>>")
def test_custom_separator_simple():
    """Тест с простым пользовательским разделителем '>>>'"""

    text = """# Урок 1
lesson: 123

>>> TEXT
## Первый шаг
Текст первого шага
много строк

>>> QUIZ
## Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
    result = ParseSchema.parse_document(text)
    # print("\n", json.dumps(result, indent=4, ensure_ascii=False))

    assert result['title'] == 'Урок 1'
    assert result['variables'] == {'lesson': '123'}
    assert len(result['steps']) == 2

    # Проверяем первый шаг
    assert result['steps'][0]['h2'] == 'TEXT'
    # assert '##  Первый шаг\nТекст первого шага' in result['steps'][0]['text']
    assert '\n## Первый шаг\nТекст первого шага\nмного строк\n' == result['steps'][0]['text']

    # Проверяем второй шаг
    assert result['steps'][1]['h2'] == 'QUIZ'
    assert '\n## Второй шаг\nВопрос?\nA. вариант 1\nB. вариант 2\nANSWER: A' == result['steps'][1]['text']


@pytest.mark.step_begin('---===$$$===---')
def test_custom_separator_with_special_chars():
    """Тест с разделителем, содержащим специальные символы"""

    text = """# Урок 1
lesson: 123

---===$$$===--- TEXT
## Первый шаг
Текст первого шага
много строк

---===$$$===--- QUIZ SKIP
## Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
    result = ParseSchema.parse_document(text)

    assert result['title'] == 'Урок 1'
    assert result['variables'] == {'lesson': '123'}
    assert len(result['steps']) == 2

    # Проверяем первый шаг
    assert result['steps'][0]['h2'] == 'TEXT'
    # assert '##  Первый шаг\nТекст первого шага' in result['steps'][0]['text']
    assert '\n## Первый шаг\nТекст первого шага\nмного строк\n' == result['steps'][0]['text']

    # Проверяем второй шаг
    assert result['steps'][1]['h2'] == 'QUIZ SKIP'
    assert '\n## Второй шаг\nВопрос?\nA. вариант 1\nB. вариант 2\nANSWER: A' == result['steps'][1]['text']


@pytest.mark.step_begin(">>>")
def test_preserve_headers_inside_step():
    """Тест, что заголовки внутри шага не воспринимаются как новые шаги"""

    text = """# Урок 1
lesson: 123

>>> TEXT
Шаг с внутренними заголовками
# Заголовок первого уровня внутри шага
## Заголовок второго уровня внутри шага
### Заголовок третьего уровня внутри шага
Обычный текст

>>> SKIP QUIZ
Следующий шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
    expected_text_step1 = """
Шаг с внутренними заголовками
# Заголовок первого уровня внутри шага
## Заголовок второго уровня внутри шага
### Заголовок третьего уровня внутри шага
Обычный текст
"""
    result = ParseSchema.parse_document(text)

    assert result['title'] == 'Урок 1'
    assert result['variables'] == {'lesson': '123'}
    assert len(result['steps']) == 2

    # Проверяем первый шаг
    assert result['steps'][0]['h2'] == 'TEXT'
    assert expected_text_step1 == result['steps'][0]['text']

    # Проверяем второй шаг
    assert result['steps'][1]['h2'] == 'SKIP QUIZ'
    assert '\nСледующий шаг\nВопрос?\nA. вариант 1\nB. вариант 2\nANSWER: A' == result['steps'][1]['text']


@pytest.mark.step_begin(">>>")
def test_no_steps():
    """Тест: урок без шагов"""
    text = """# Урок без шагов
lesson: 123
"""
    result = ParseSchema.parse_document(text)

    assert result["title"] == "Урок без шагов"
    assert result["variables"] == {"lesson": "123"}
    assert len(result["steps"]) == 0  # Нет шагов


@pytest.mark.parametrize(
    "separator",
    [
        "==>",
        "---",
        "***",
        "###",
        "$$$",
        "@@@",
        "step:",
        "-->>",
        "::::",
    ],
)
def test_various_separators(separator):
    """Параметризованный тест с разными разделителями"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = separator

    try:
        text = f"""# Урок 1
lesson: 123

{separator} TEXT Первый шаг
Текст первого шага

{separator} QUIZ Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result["steps"]) == 2
        assert result["steps"][0]["h2"] == "TEXT Первый шаг"
        assert result["steps"][1]["h2"] == "QUIZ Второй шаг"

    finally:
        settings.STEP_BEGIN = old_separator


def test_separator_with_numbers():
    """Тест с разделителем, содержащим цифры"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = "12345"

    try:
        text = """# Урок 1
lesson: 123

12345 TEXT
Первый шаг
Текст первого шага

12345 QUIZ
Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result["steps"]) == 2
        assert result["steps"][0]["h2"] == "TEXT"
        assert result["steps"][1]["h2"] == "QUIZ"

    finally:
        settings.STEP_BEGIN = old_separator


def test_very_long_separator():
    """Тест с очень длинным разделителем"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = "=" * 50

    try:
        text = f"""# Урок 1
lesson: 123

{'=' * 50} TEXT
Первый шаг
Текст первого шага

{'=' * 50} QUIZ
Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result["steps"]) == 2
        assert result["steps"][0]["h2"] == "TEXT"
        assert result["steps"][1]["h2"] == "QUIZ"

    finally:
        settings.STEP_BEGIN = old_separator


if __name__ == "__main__":
    # Если файл запущен напрямую, запускаем тесты через pytest
    print("Запуск тестов...")
    pytest.main([__file__, "-v"])
