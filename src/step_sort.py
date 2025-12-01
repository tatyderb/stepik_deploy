"""
Разбор шага типа SORT - задача на сортировку.

https://stepik.org/lesson/385335/
{
    "block":{
        "text":"Вы можете изменить условие задания в этом поле и указать настройки ниже.",
        "name":"sorting",
        "video":null,
        "options":null,
        "source": {
            "is_html_enabled":true,
            "options": [
                {
                    "text":"One"
                },
                {
                    "text":"Two"
                },
                {
                    "text":"Three"
                }
            ]
        }
    },
    "id":null,
    "has_review":false,
    "time":"2025-11-22T20:13:34.776Z"
}

"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepSort(Step):
    DEFAULT_SCORE = 2
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': 'Условие задачи',
                'name': 'sorting',
                'source': {
                    'options': [],  # перечисление ответов
                    'is_html_enabled': True
                }
            },
            'lesson': None,
            'position': None,
            'cost': DEFAULT_SCORE
        }
    }

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepSort.parse_step_sort(text)
        print(f'StepSort.parse: {res=}')

        self.text = self.h2() + res['text']
        self.options = res['options']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        d['stepSource']['block']['source']['options'] = self.options
        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            else:
                option = self.config[key]
                d['stepSource']['block']['source'][key] = ParseSchema.to_boolean(option)
        return d


class ParseSchemaStepSort(ParseSchema):
    @classmethod
    def step_sort(cls) -> pp.ParserElement:
        """
        Условие
        SORT
        Первый пункт
        ====
        Второй пункт
        ====
        CONFIG
        score: 3
        to dict
        {'text': 'Условие', 'options': [{'text': 'Первый пункт'}, {'text': 'Второй пункт'}], 'config': {'score': '3'}}
        """
        config = cls.config()('config')

        keyword = pp.LineStart() + "SORT"
        description = pp.SkipTo(keyword).setParseAction(lambda t: t[0].strip())("text")

        separator = pp.AtLineStart(pp.Word('=', min=4)) + pp.LineEnd().suppress()

        option_text = pp.SkipTo(separator).setParseAction(lambda t: t[0].strip()) + pp.Optional(pp.LineEnd().suppress())
        option = option_text.setParseAction(lambda t: {"text": t[0]})

        options = pp.delimitedList(option, delim=separator, allow_trailing_delim=True)("options")

        schema = pp.Optional(description) + keyword + options + pp.Optional(config)

        return schema

    @classmethod
    def parse_step_sort(cls, text: str) -> ParseResults:
        try:
            return cls.step_sort().parseString(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
