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

"""

import pyparsing as pp

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html

from src.dump import BaseNotImplementedExporter


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

    DEFAULT_COMPONENT_TEXT = {
        "type": "text",
        "text": "",
        "options": []
    }

    DEFAULT_COMPONENT_INPUT_SELECT = {
        "type": "",  # будет заполнено позже: "input" или "select"
        "text": "",
        "options": []  # будет заполнено списком вариантов
    }

    DEFAULT_OPTION = {
        "text": "",
        "is_correct": False
    }

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepSpace.parse_step_space(text)
        print(f'StepSpace.parse: {res=}')

        self.text = self.h2()

        # res состоит из списка с text/input/select и словаря с настройками в конце (опционально)
        if res and isinstance(res[-1], dict):
            self.config = res[-1]
            self.space_or_text = res[:-1]
        else:

            self.config = {}
            self.space_or_text = res

    def to_dict(self) -> dict:
        from copy import deepcopy
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)

        components = []
        for item in self.space_or_text:
            if isinstance(item, str):
                component = deepcopy(self.DEFAULT_COMPONENT_TEXT)

                # Согласно https://stepik.org/lesson/385339/step/4?unit=374784
                # для переноса строки нужно использовать <br>
                component["text"] = item.replace("\n", "<br>")

                components.append(component)

            elif isinstance(item, list):
                component = deepcopy(self.DEFAULT_COMPONENT_INPUT_SELECT)

                options_list = []
                for option in item:
                    # опции парсятся в следующем формате:
                    # ['Пётр I'] правильный вариант
                    # ['*', 'Николай II'] неправильный

                    option_template = deepcopy(self.DEFAULT_OPTION)
                    option_template["text"] = option[-1]
                    option_template["is_correct"] = len(option) == 1
                    options_list.append(option_template)

                # Если все опции верные, то определяем тип как input (без выпадающего списка)
                # Иначе выпадающий список select
                component["type"] = "input" if all(
                    opt["is_correct"] for opt in options_list) else "select"
                component["options"] = options_list

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

        empty_text = pp.Empty().set_parse_action(lambda: "")
        option_text.set_parse_action(
            lambda t: [t[0].replace('\]', ']', -1)]
        )
        option_text_or_empty = option_text ^ empty_text

        answer_option = pp.Group(
            (pp.Optional(error_marker)("marker") +
             pp.Suppress(pp.Literal("[")) +
             option_text_or_empty("text") +
             pp.Suppress(pp.Literal("]")))
        )

        answer_list = pp.Group(
            pp.Suppress(pp.Literal("<")) +
            pp.DelimitedList(answer_option) +
            pp.Suppress(pp.Literal(">"))
        )

        config = cls.config()('config')
        sections = answer_list & pp.Optional(config)
        text_bound = cls.quoted() | sections
        text_part = pp.SkipTo(text_bound)

        schema = pp.ZeroOrMore(answer_list("SPACE") ^ text_part("TEXT")) \
            + pp.Optional(pp.SkipTo(config | pp.StringEnd())
                          )("TEXT") + pp.Optional(config)

        return schema

    @classmethod
    def parse_step_space(cls, text: str) -> list:
        try:
            return cls.step_space().parse_string(text, parse_all=True).as_list()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)


class SpaceDump(BaseNotImplementedExporter):
    """Заглушка для SPACE шагов"""
    pass
