"""
Разбор шага типа MATCH - задача на сопоставление.

https://stepik.org/lesson/385336/
{
    "block":{
        "text":"Вы можете изменить условие задания в этом поле и указать настройки ниже.",
        "name":"matching",
        "video":null,
        "options":{},
        "subtitle_files":[],
        "is_deprecated":false,
        "source": {
            "preserve_firsts_order":true
            "is_html_enabled":true,
            "pairs": [
                {
                    "first":"Sky",
                    "second":"Blue"
                },
                {
                    "first":"Sun",
                    "second":"Orange"
                },
                {
                    "first":"Grass",
                    "second":"Green"
                }
            ]
        }
        "subtitles":{}
    },
    "id":null,
    "has_review":false,
    "time":"2026-02-19T13:43:37.903Z"
}



"""

# {"block":{"source":{"pairs":[,]},"tests_archive":null,"feedback_correct":"","feedback_wrong":""},"id":"9558981","has_review":false,"time":"2026-02-19T13:43:37.903Z"}

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepMatch(Step):
    DEFAULT_SCORE = 1
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': 'Условие задачи',
                'name': 'matching',
                'video': None,
                'options': {},
                'source': {
                    'preserve_firsts_order': True,
                    'is_html_enabled': True,
                    'pairs': []
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
        res = ParseSchemaStepMatch.parse_step_match(text)
        print(f'StepMatch.parse: {res=}')

        self.text = self.h2() + res['text']
        self.pairs = res['pairs']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        d['stepSource']['block']['source']['pairs'] = self.pairs
        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            elif key == 'is_randomize':
                option = self.config[key]
                d['stepSource']['block']['source']['preserve_firsts_order'] = not ParseSchema.to_boolean(
                    option)
            elif key == 'html':
                option = self.config[key]
                d['stepSource']['block']['source']['is_html_enabled'] = ParseSchema.to_boolean(
                    option)
            else:
                option = self.config[key]
                d['stepSource']['block']['source'][key] = ParseSchema.to_boolean(
                    option)
        return d


class ParseSchemaStepMatch(ParseSchema):
    @classmethod
    def step_match(cls) -> pp.ParserElement:
        """
        Условие
        MATCH
        Пункт 1
        ----
        Значение, соответствующее пункту 1
        ====
        Пункт 2
        ----
        Значение, соответствующее пункту 2
        ====
        Пункт 3
        ----
        Значение, соответствующее пункту 3
        ====
        CONFIG
        score: 3
        to dict
        {'text': 'Условие\n', 'pairs': [{'first': 'Пункт 1', 'second': 'Значение, соответствующее пункту 1'}, {'first': 'Пункт 2', 'second': 'Значение, соответствующее пункту 2'}, {'first': 'Пункт 3', 'second': 'Значение, соответствующее пункту 3'}], 'config': {'score': '3'}}
        """
        keyword = pp.LineStart() + "MATCH"

        separator = pp.AtLineStart(
            pp.Word('=', min=4)) + pp.LineEnd().suppress()
        separator_in_pair = pp.AtLineStart(
            pp.Word('-', min=4)) + pp.LineEnd().suppress()

        pair = pp.Group(
            pp.SkipTo(separator_in_pair).set_parse_action(lambda t: t[0].strip()) +
            pp.Suppress(separator_in_pair) +
            pp.SkipTo(separator).set_parse_action(lambda t: t[0].strip())
        ).set_parse_action(lambda t: {"first": t[0][0], "second": t[0][1]})

        pairs = keyword + \
            pp.DelimitedList(pair, delim=separator,
                             allow_trailing_delim=True)("pairs")

        config = cls.config()('config')

        sections = pairs & pp.Opt(config)

        text_bound = cls.quoted() | sections

        text_part = pp.SkipTo(text_bound)

        statement = (text_part + pp.ZeroOrMore(cls.quoted + text_part)).set_parse_action(
            lambda toks: ''.join(toks)
        )("text")

        schema = statement + sections
        return schema

    @classmethod
    def parse_step_match(cls, text: str) -> ParseResults:
        try:
            return cls.step_match().parse_string(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
