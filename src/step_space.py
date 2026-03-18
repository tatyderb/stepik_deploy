"""
Разбор шага типа SPACE - задача на пропуски.

https://stepik.org/lesson/385339/
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

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepSpace(Step):
    DEFAULT_SCORE = 2
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': '',
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
        res = ParseSchemaStepSpace.parse_step_space(text)
        print(f'StepSpace.parse: {res=}')

        self.text = self.h2() 

        if res and isinstance(res[-1], dict):
            self.config = res[-1]
            self.space_or_text = res[:-1]
        else:
            self.config = {}
            self.space_or_text = res

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        

        components = []
        for item in self.space_or_text:
            if isinstance(item, str):
                # print(f"{item = }")
                component = {
                    "type": "text",
                    "text": markdown_to_html(item),
                    "options": []
                }
                components.append(component)
                
            elif isinstance(item, list):
                 
                options_list = []
                
                for option in item:
                    options_list.append({
                        "text": option[-1],
                        "is_correct": len(option) == 1
                    })
                    
                component = {
                    "type": "input" if all(option["is_correct"] for option in options_list) else "select",
                    "text": "",
                    "options": options_list
                }
                components.append(component)
    
        d['stepSource']['block']['source']['components'] = components


        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            elif key == 'case_sensitive':
                option = self.config[key]
                d['stepSource']['block']['source']['is_case_sensitive'] = ParseSchema.to_boolean(
                    option)
            elif key == 'visual_feedback':
                option = self.config[key]
                d['stepSource']['block']['source']['is_detailed_feedback'] = ParseSchema.to_boolean(
                    option)
            elif key == 'partial_correct':
                option = self.config[key]
                d['stepSource']['block']['source']['is_partially_correct'] = ParseSchema.to_boolean(
                    option)
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

        empty_text = pp.Empty().setParseAction(lambda: "")
        option_text_or_empty = pp.Or([option_text, empty_text])


        answer_option = pp.Group(
            (pp.Optional(error_marker)("marker") +
            pp.Literal("[").suppress() + 
            option_text_or_empty("text") + 
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
        text_part.setParseAction(
            lambda t: [t[0].replace('\]', ']', -1)]
        )

        schema = pp.ZeroOrMore(pp.Or([answer_list("SPACE"), text_part("TEXT")])) \
            + pp.Optional(pp.SkipTo(config | pp.StringEnd()))("TEXT") + pp.Optional(config)

        return schema

    @classmethod
    def parse_step_space(cls, text: str) -> list:
        try:
            return cls.step_space().parse_string(text, parse_all=True).as_list()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
