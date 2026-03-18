"""
Разбор шага типа SPACE - задача на сортировку.

https://stepik.org/lesson/385335/
{
    "block": {
        "name":"fill-blanks",
        "text":"Вы можете изменить условие задания в этом поле и указать настройки ниже.",
        "video":null,
        "options":{},
        "subtitle_files":[],
        "is_deprecated":false,
        "source": {
            "components":[
            {
                "type":"text",
                "text":"Поэму \"Медный всадник\" написал ",
                "options":[]
            },
            {
                "type":"input",
                "text":"",
                "options":[
                    {"text":"Пушкин","is_correct":true},
                    {"text":"А.С. Пушкин","is_correct":true},
                    {"text":"А. С. Пушкин","is_correct":true},
                    {"text":"[Александр Сергеевич Пушкин","is_correct":true}
                ]
            },
            {
                "type":"text",
                "text":"Поэму \"Кому на Руси жить хорошо\" написал ",
                "options":[]
            },
            {
                "type":"select",
                "text":"",
                "options":[
                    {"text":"Пушкин","is_correct":false},
                    {"text":"Тургеньев","is_correct":false},
                    {"text":"Некрасов","is_correct":true}
                ]
            }
            ],
            "is_case_sensitive":false,
            "is_detailed_feedback":false,
            "is_partially_correct":false
        },
        "subtitles":{},
        "tests_archive":null,
        "feedback_correct":"",
        "feedback_wrong":""
    }
    "id":null,
    "has_review":false,
    "time":"2025-11-22T20:13:34.776Z"
}


{"block":{"name":"fill-blanks","text":"Вы можете изменить условие задания в этом поле и указать настройки ниже.","video":null,"options":{},"subtitle_files":[],"is_deprecated":false,"source":{"components":[{"type":"text","text":"Поэму \"Медный всадник\" написал ","options":[]},{"type":"input","text":"","options":[{"text":"Пушкин","is_correct":true},{"text":"А.С. Пушкин","is_correct":true},{"text":"А. С. Пушкин","is_correct":true},{"text":"[Александр Сергеевич Пушкин","is_correct":true}]},{"type":"text","text":"Поэму \"Кому на Руси жить хорошо\" написал ","options":[]},{"type":"select","text":"","options":[{"text":"Пушкин","is_correct":false},{"text":"Тургеньев","is_correct":false},{"text":"Некрасов","is_correct":true}]}],"is_case_sensitive":false,"is_detailed_feedback":false,"is_partially_correct":false},"subtitles":{},"tests_archive":null,"feedback_correct":"","feedback_wrong":""},"id":"9627339","has_review":false,"time":"2026-03-12T23:14:10.494Z"}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepSpace(Step):
    DEFAULT_SCORE = 2
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': 'Условие задачи',
                'name': 'fill-blanks',
                'source': {
                    'components': [],
                    "is_case_sensitive": False,
                    "is_detailed_feedback": False,
                    "is_partially_correct": False
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
        res = ParseSchemaStepSpace.parse_step_sort(text)
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
                d['stepSource']['block']['source'][key] = ParseSchema.to_boolean(
                    option)
        return d


class ParseSchemaStepSpace(ParseSchema):
    @classmethod
    def step_space(cls) -> pp.ParserElement:
        """
        '''
        Поэму "Кому на Руси жить хорошо" написал <*[Пушкин], *[Тургеньев], [Некрасов]>
        CONFIG
        score: 3
        '''
        to list
        ['Поэму "Кому на Руси жить хорошо" написал', [['*', 'Пушкин'], ['*', 'Тургеньев'], ['Некрасов']], '', {'score': '3'}]
        """
        error_marker = pp.Literal("*")
        option_text = pp.Regex(r'(?:[^\]\\]|\\.)+')


        answer_option = pp.Group(
            (pp.Optional(error_marker)("marker") +
            pp.Literal("[").suppress() + 
            option_text("text") + 
            pp.Literal("]").suppress())
        )

        answer_list = pp.Group(
            pp.Literal("<").suppress() + 
            pp.DelimitedList(answer_option) + 
            pp.Literal(">").suppress()
        )

        config = cls.config()('config')
        sections = answer_list & pp.Opt(config)
        text_bound = cls.quoted() | sections
        text_part = pp.SkipTo(text_bound)

        schema = pp.ZeroOrMore(pp.Or([answer_list("SPACE"), text_part("TEXT")])) \
            + pp.Optional(pp.SkipTo(config | pp.LineEnd()))("TEXT") + pp.Optional(config)

        return schema

    @classmethod
    def parse_step_space(cls, text: str) -> list:
        try:
            return cls.step_space().parse_string(text, parse_all=True).as_list()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
