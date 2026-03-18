import pytest

from src.step_space import ParseSchemaStepSpace


@pytest.fixture
def parser():
    return ParseSchemaStepSpace


class TestParseSchemaStepSpace:

    def test_simple_text_only(self, parser):
        text = "Просто текст без ответов"
        result = parser.parse_step_space(text)
        expected = ['Просто текст без ответов']
        assert result == expected

    def test_only_answers_all_correct(self, parser):
        text = "<[Первый], [Второй], [Третий]>"
        result = parser.parse_step_space(text)
        expected = [[['Первый'], ['Второй'], ['Третий']], ""]
        assert result == expected

    def test_only_answers_with_incorrect(self, parser):
        text = "<*[Первый], [Второй], *[Третий]>"
        result = parser.parse_step_space(text)
        expected = [[['*', 'Первый'], ['Второй'], ['*', 'Третий']], ""]
        assert result == expected

    def test_text_before_answers(self, parser):
        """Тест с текстом перед блоком ответов"""
        text = 'Поэму "Кому на Руси жить хорошо" написал <[Некрасов]>'
        result = parser.parse_step_space(text)
        expected = ['Поэму "Кому на Руси жить хорошо" написал',  [['Некрасов']], ""]
        assert result == expected

    def test_text_after_answers(self, parser):
        text = "<[Пушкин]> и другие поэты"
        result = parser.parse_step_space(text)
        expected = [[['Пушкин']], " и другие поэты"]
        assert result == expected

    def test_multiple_answer_blocks(self, parser):
        text = 'Начало <[А], [Б]> середина <[В], *[Г]> конец'
        result = parser.parse_step_space(text)
        print(result)
        expected = ['Начало', [['А'], ['Б']], ' середина', [['В'], ['*', 'Г']], ' конец']
        assert result == expected
