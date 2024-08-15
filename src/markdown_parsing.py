import pyparsing as pp
import sys

import src.step as step


_PARSE_ERROR_EXIT_CODE = 1


def parse_error(line_number: int = -1, line: str = '', error_msg: str = '', exit_program: bool = True):
    print(f'{error_msg}\n{line_number}: <{line}>', file=sys.stderr)
    if exit_program:
        sys.exit(_PARSE_ERROR_EXIT_CODE)


class ParseSchema:
    __step_types = step.Step.STEP_TYPES
    __skip_keyword = 'SKIP'
    __markdown_variables = ['lesson', 'lang']

    @classmethod
    def h1(cls) -> pp.ParserElement:
        lesson_title = pp.rest_of_line()('title')
        lesson_module = pp.Suppress(pp.Keyword('#') + pp.White()[1, ...]) + lesson_title
        return lesson_module

    @classmethod
    def parse_h1(cls, line: str) -> str:
        """Scheme '# title' to title."""
        try:
            return ParseSchema.h1().parseString(line).title
        except pp.ParseException:
            parse_error(1, line, 'Expect H1 line started with # and space symbol.')


    @classmethod
    def variable_value(cls) -> pp.ParserElement:
        """Scheme 'variable = value' to (variable_str, value_str)"""
        variable = pp.one_of(cls.__markdown_variables, as_keyword=True)('variable')
        value = pp.rest_of_line()('value')
        configure_set = variable + pp.Suppress('=' + pp.White()[...]) + value
        return configure_set

    @classmethod
    def parse_variable_value(cls, line: str) -> (bool, str, str):
        try:
            res = cls.variable_value().parseString(line)
            return True, res.variable, res.value.strip()
        except pp.ParseException:
            return False, None, None

    @classmethod
    def step_header(cls) -> pp.ParserElement:
        """Scheme '## [[SKIP] TYPE] header' to (type, header, skip)"""
        step_type = pp.one_of(cls.__step_types, as_keyword=True)('type')
        header = pp.rest_of_line()('header')
        skip = pp.Keyword(cls.__skip_keyword)('skip')
        step_module = pp.Suppress('##' + pp.White()[1, ...]) + skip[0, 1] + step_type[0, 1] + skip[0, 1] + header
        return step_module

    @classmethod
    def parse_step_header(cls, line: str) -> (bool, bool, str, str):
        """Разбор заголовка шага.'## [[SKIP] TYPE] header' to (ok, skip, type, header)"""
        # ожидаем ## в начале строки! Иначе мы не можем гарантировать, что не встретим ## в середине шага
        if not line.startswith('##'):
            return False, False, None, ''

        try:
            res = cls.step_header().parseString(line)
            return True, res.skip == 'SKIP', res.type, res.header.strip()
        except pp.ParseException:
            return False, False, None, ''







