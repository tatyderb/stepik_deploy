import pyparsing as pp
import sys

from pyparsing import ParseException

from src.settings import settings
import src.step as step


_PARSE_ERROR_EXIT_CODE = 1


def parse_error(line_number: int = -1, line: str = '', error_msg: str = '', exit_program: bool = True):

    line_number_str = f'{line_number}: ' if line_number >= 0 else ''
    displayed_line = f'{line_number_str}<{line}>' if line else ''
    print(f'{error_msg}\n{displayed_line}', file=sys.stderr)
    if exit_program:
        sys.exit(_PARSE_ERROR_EXIT_CODE)


class ParseSchema:
    __step_types = step.Step.STEP_TYPES
    __skip_keyword = 'SKIP'
    __markdown_variables = ['lesson', 'lang']
    # символы, допустимые в значении переменных
    __variable_value_chars = pp.alphanums + '._-'
    # number_int = pp.Combine(pp.Opt('-') + pp.Word(pp.nums))('int')
    # number_float = pp.Combine(pp.Opt('-') + pp.Word(pp.nums) + '.' + pp.Word(pp.nums))('float')
    # number = (number_float | number_int)('number')
    number = pp.common.number
    quoted = pp.QuotedString('```', multiline=True, unquote_results=False)
    # TODO: не надо ограничивать, только кидать предупреждение, что разобранный язык не в списке и добавлять по возможности,
    #  список языков держать в файле конфигурации
    LANGUAGE = ['c', 'c_valgrind', 'python', 'python310']

    @classmethod
    def to_number(cls, text: str) -> int | float:
        """Преобразует строку в int или float. Убедитесь сначала, что это число."""
        return float(text) if '.' in text else int(text)

    @classmethod
    def to_boolean(cls, word: str) -> bool:
        """Преобразует слово в bool. Доступны несколько вариантов"""
        true_values = ["true", "1", "yes", "on",
                       "y", "enable", "да", "вкл", "+"]
        false_values = ["false", "0", "no", "off",
                        "n", "disable", "нет", "выкл", "-"]

        true_parser = pp.one_of(
            true_values, caseless=True).set_parse_action(lambda: True)
        false_parser = pp.one_of(
            false_values, caseless=True).set_parse_action(lambda: False)

        bool_parser = true_parser | false_parser

        try:
            result = bool_parser.parse_string(word.strip())
            return result[0]
        except pp.ParseException:
            raise ValueError(
                f"Невозможно преобразовать '{word}' в булево значение")

    @classmethod
    def variables(cls) -> pp.ParserElement:
        """
        Parse schema for text with
        variable1 = value1
        or
        variable2 : value2
        return
        {variable1: value1, variable2, value2}
        """

        # identifier = pp.one_of(cls.__markdown_variables)('identifier')
        identifier = pp.Word(pp.alphanums + '_')('identifier')
        equals = (pp.Literal("=") | (pp.Literal(':'))).suppress()
        value = pp.Word(cls.__variable_value_chars)('value')
        assignment = pp.Group(identifier + equals +
                              value + pp.restOfLine().suppress())
        lesson_variables = pp.Dict(pp.ZeroOrMore(assignment))
        return lesson_variables

    @classmethod
    def parse_variables(cls, text: str, default_values: dict | None = None, test_mode: bool = False):
        """
        Parse text with
        variable1 = value1
        or
        variable2 : value2
        return
        {variable1: value1, variable2, value2},
        допустимы только переменные из default_values: если None, то допустимы любые переменные,
        иначе берет из указанных переменных значения по умолчанию для тех переменных, что не заданы.
        """
        try:
            d = cls.variables().parse_string(text, parse_all=True).asDict()
            if default_values is None:
                return d

            vars = set(d.keys())
            vars_allow = set(default_values.keys())
            unexpected_vars = vars - vars_allow
            if unexpected_vars:
                parse_error(
                    line='text', error_msg=f'Unexpected variables {unexpected_vars}')
            # берем значения по умолчанию и дополняем разобранными
            dres = default_values.copy()
            dres.update(d)
            return dres

        except ParseException as e:
            # в тестах проверяем, что схема ловит проблему
            if test_mode:
                raise e
            # вне теста выводим сообщление об ошибке
            parse_error(line=text, error_msg=e.msg)

    @classmethod
    def section_name(cls, name: str) -> pp.ParserElement:
        return pp.AtLineStart(name) + pp.LineEnd()

    @classmethod
    def config(cls) -> pp.ParserElement:
        """
        Parsing schema for:
        CONFIG
        var1: val1
        var2: val2
        """
        section_title = cls.section_name('CONFIG')
        schema = pp.Suppress(section_title) + cls.variables()('config')
        # тест test_markdown.py::test_config получает не список, а значение, set_parse_action не нужно тогда
        schema.set_parse_action(lambda t: t.as_dict()['config'][0])
        return schema

    @classmethod
    def variable_value(cls) -> pp.ParserElement:
        # TODO: убрать, так как есть схема variables
        """Scheme 'variable = value' to (variable_str, value_str)"""
        variable = pp.one_of(cls.__markdown_variables,
                             as_keyword=True)('variable')
        value = pp.rest_of_line()('value')
        sign = (pp.Literal('=') | pp.Literal(':'))
        configure_set = variable + pp.Suppress(sign + pp.White()[...]) + value
        return configure_set

    @classmethod
    def document(cls) -> pp.ParserElement:
        """
        Возвращает схему для разбора на блоки (потом будем разбирать каждый блок отдельно)
        # Заголовок урока
        lesson_id: 123
        lang: c_valgrind
        STEP_BEGIN QUIZ Формат вывода
        текст шага
        STEP_BEGIN SKIP SORT Типы данных
        текст шага
        """

        # Определяем грамматику
        h1_header = pp.LineStart() + "#" + pp.Suppress(pp.White()) + \
            pp.restOfLine("h1_header")  # Заголовок уровня 1
        h2_header = pp.LineStart() + settings.STEP_BEGIN + pp.Suppress(pp.White()) + \
            pp.restOfLine(
                "h2_header")  # Заголовок уровня 2# Заголовок уровня 2

        # Текст до следующего заголовка или конца документа с учетом settings.STEP_BEGIN внутри вставок кода
        text_bound = cls.quoted | h2_header | pp.stringEnd()
        text_part = pp.SkipTo(text_bound)
        text = (text_part + pp.ZeroOrMore(cls.quoted + text_part))("text")
        # лишние \n будут убраны при конвертации в html, а недостающие \n могут испортить формат markdown
        text.set_parse_action(lambda t: '\n'.join(t.text))
        # text = pp.SkipTo(h2_header | pp.stringEnd)("text")
        # text = pp.SkipTo(h1_header | pp.stringEnd)("text")

        # Элементы документа
        h1_entry = h1_header + text
        # h1_entry.set_parse_action(cls.parse_lesson_variables)
        h1_entry.set_parse_action(lambda t: {
                                  'title': t.h1_header, 'variables': cls.variables().parse_string(t.text).asDict()})
        # h1_entry.set_parse_action(lambda t: {'h1': t.h1_header, 'text': t.text})

        h2_entry = h2_header + text
        h2_entry.set_parse_action(
            lambda t: {'h2': t.h2_header, 'text': t.text})

        # Весь документ может содержать любую комбинацию этих элементов
        markdown_document = h1_entry + pp.ZeroOrMore(h2_entry)

        def format_data(t: list[dict]):
            d = t[0]
            d['steps'] = t[1:]
            return d
        # markdown_document.set_parse_action(lambda t: print(f'{t=}') or format_data(t))
        markdown_document.set_parse_action(lambda t: format_data(t))
        return markdown_document

    @classmethod
    def parse_document(cls, line: str) -> dict:
        """Разбивает файл на крупные блоки и возвращает их в формате
        @TODO: проверять, что переменные из списка, если еще какие - сообщение об ошибке
        {
        'title': lesson_header,
        'variables': {
            'lesson_id': 1234,
            'lang': None,
        },
        steps: [
            {'h2': 'QUIZ Формат вывода', 'text': 'длинный текст на много строк в markdown'},
            {'h2': 'SKIP SORT Типы данных', 'text': 'длинный текст на много строк в markdown'}
        ]}
        """
        try:
            return ParseSchema.document().parse_string(line).as_list()[0]
        except pp.ParseException:
            parse_error(
                1, line, 'Expect H1 line started with # and space symbol.')

    @classmethod
    def step_header(cls) -> pp.ParserElement:
        """Scheme 'STEP_BEGIN [[SKIP] TYPE] header' to (type, header, skip)"""
        step_type = pp.one_of(cls.__step_types, as_keyword=True)('type')
        header = pp.rest_of_line()('header')
        skip = pp.Keyword(cls.__skip_keyword)('skip')
        # step_module = pp.Suppress('##' + pp.White()[1, ...]) + skip[0, 1] + step_type[0, 1] + skip[0, 1] + header
        step_module = skip[0, 1] + step_type[0, 1] + skip[0, 1] + header
        return step_module

    @classmethod
    def parse_step_header(cls, line: str) -> tuple[bool, bool, str, str]:
        """Разбор заголовка шага.'STEP_BEGIN [[SKIP] TYPE] header' to (ok, skip, type, header)"""
        try:
            res = cls.step_header().parse_string(line).asDict()
            # print(f"parse_step_header: <{line}> {res=}")
            # TEXT type by default
            if 'type' not in res:
                res['type'] = 'TEXT'
            return True, res['type'], 'skip' in res, res['header'].strip()
        except pp.ParseException:

            return False, False, None, ''
