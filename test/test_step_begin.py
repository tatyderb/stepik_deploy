"""Тесты для проверки работы с разными разделителями шагов."""

import pytest

import sys
from pathlib import Path

from src.markdown_parsing import ParseSchema
from src.settings import settings


# Добавляем корневую директорию проекта в путь импорта
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_default_separator():
    """Тест с разделителем по умолчанию '##'"""
    # Сохраняем текущее значение
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '##'

    try:
        text = """# Урок 1
lesson: 123

## TEXT Первый шаг
Текст первого шага
много строк

## QUIZ Второй шаг
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
        assert result['steps'][0]['h2'] == 'TEXT Первый шаг'
        assert 'Текст первого шага' in result['steps'][0]['text']

        # Проверяем второй шаг
        assert result['steps'][1]['h2'] == 'QUIZ Второй шаг'
        assert 'Вопрос?' in result['steps'][1]['text']
        assert 'A. вариант 1' in result['steps'][1]['text']

    finally:
        # Восстанавливаем значение
        settings.STEP_BEGIN = old_separator


def test_custom_separator_simple():
    """Тест с простым пользовательским разделителем '>>>'"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '>>>'

    try:
        text = """# Урок 1
lesson: 123

>>> TEXT Первый шаг
Текст первого шага
много строк

>>> QUIZ Второй шаг
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
        assert result['steps'][0]['h2'] == 'TEXT Первый шаг'
        assert 'Текст первого шага' in result['steps'][0]['text']

        # Проверяем второй шаг
        assert result['steps'][1]['h2'] == 'QUIZ Второй шаг'
        assert 'Вопрос?' in result['steps'][1]['text']

    finally:
        settings.STEP_BEGIN = old_separator


def test_custom_separator_with_special_chars():
    """Тест с разделителем, содержащим специальные символы"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '---===$$$===---'

    try:
        text = """# Урок 1
lesson: 123

---===$$$===--- TEXT Первый шаг
Текст первого шага

---===$$$===--- QUIZ Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result['steps']) == 2
        assert result['steps'][0]['h2'] == 'TEXT Первый шаг'
        assert result['steps'][1]['h2'] == 'QUIZ Второй шаг'

    finally:
        settings.STEP_BEGIN = old_separator


def test_mixed_separators_in_one_file():
    """Тест: разные разделители в одном файле - должен работать первый"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '>>>'

    try:
        text = """# Урок 1
lesson: 123

>>> TEXT Первый шаг
Текст первого шага

## QUIZ Второй шаг  # этот не должен быть распознан как шаг!
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        # Должен быть только один шаг, потому что '##' не распознается как разделитель
        assert len(result['steps']) == 1
        assert result['steps'][0]['h2'] == 'TEXT Первый шаг'

        # Проверяем, что '## QUIZ' осталось в тексте первого шага
        assert '## QUIZ Второй шаг' in result['steps'][0]['text']

    finally:
        settings.STEP_BEGIN = old_separator


def test_separator_with_hash_symbol():
    """Тест с разделителем, содержащим символ # (требует пробелов после)"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '###'

    try:
        text = """# Урок 1
lesson: 123

### TEXT Первый шаг
Текст первого шага

### QUIZ Второй шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result['steps']) == 2
        assert result['steps'][0]['h2'] == 'TEXT Первый шаг'
        assert result['steps'][1]['h2'] == 'QUIZ Второй шаг'

    finally:
        settings.STEP_BEGIN = old_separator


def test_preserve_headers_inside_step():
    """Тест, что заголовки внутри шага не воспринимаются как новые шаги"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = '>>>'

    try:
        text = """# Урок 1
lesson: 123

>>> TEXT Шаг с внутренними заголовками
# Заголовок первого уровня внутри шага
## Заголовок второго уровня внутри шага
### Заголовок третьего уровня внутри шага
Обычный текст

>>> QUIZ Следующий шаг
Вопрос?
A. вариант 1
B. вариант 2
ANSWER: A
"""
        result = ParseSchema.parse_document(text)

        assert len(result['steps']) == 2

        # Проверяем, что внутренние заголовки остались в тексте
        assert '# Заголовок первого уровня внутри шага' in result['steps'][0]['text']
        assert '## Заголовок второго уровня внутри шага' in result['steps'][0]['text']
        assert '### Заголовок третьего уровня внутри шага' in result['steps'][0]['text']

    finally:
        settings.STEP_BEGIN = old_separator


def test_no_steps():
    """Тест: урок без шагов"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = ">>>"

    try:
        text = """# Урок без шагов
lesson: 123
"""
        result = ParseSchema.parse_document(text)

        assert result["title"] == "Урок без шагов"
        assert result["variables"] == {"lesson": "123"}
        assert len(result["steps"]) == 0  # Нет шагов

    finally:
        settings.STEP_BEGIN = old_separator


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

12345 TEXT Первый шаг
Текст первого шага

12345 QUIZ Второй шаг
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


def test_very_long_separator():
    """Тест с очень длинным разделителем"""
    old_separator = settings.STEP_BEGIN
    settings.STEP_BEGIN = "=" * 50

    try:
        text = f"""# Урок 1
lesson: 123

{'=' * 50} TEXT Первый шаг
Текст первого шага

{'=' * 50} QUIZ Второй шаг
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


if __name__ == "__main__":
    # Если файл запущен напрямую, запускаем тесты через pytest
    print("Запуск тестов...")
    pytest.main([__file__, "-v"])
