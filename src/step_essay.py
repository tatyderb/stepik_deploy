"""
Разбор шага типа ESSAY - ввод числа.

https://stepik.org/lesson/308224/step/9
{
  "block": {
    "text": "Вы можете изменить условие задания в этом поле и указать настройки ниже.",
    "name": "free-answer",
    "video": null,
    "options": null,
    "source": {
      "is_attachments_enabled": false,
      "is_html_enabled": true,
      "manual_scoring": false
    }
  },
  "id": null,
  "has_review": false,
  "time": "2025-10-01T16:49:10.600Z"
}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html


class StepEssay(Step):
    DEFAULT_SCORE = 1
    DEFAULT_BODY = {
        'stepSource': {
            "block": {
                "text": "Вы можете изменить условие задания в этом поле и указать настройки ниже.",
                "name": "free-answer",
                "video": None,
                "options": None,
                "source": {
                    "is_attachments_enabled": False,
                    "is_html_enabled": True,
                    "manual_scoring": False
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
        res = ParseSchemaStepEssay.parse_step_essay(text)
        print(f'StepEssay.parse: {res=}')

        self.text = self.h2() + res['text']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        from copy import deepcopy
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            else:
                option = self.config[key]
                d['stepSource']['block']['source'][key] = ParseSchema.to_boolean(option)
        return d


class ParseSchemaStepEssay(ParseSchema):

    @classmethod
    def step_essay(cls) -> pp.ParserElement:
        """
        text
        Условие задачи.
        CONFIG
        score: 5
        to dict
        {
            'text': 'Условие задачи.',
            'config': 
            {
                'score': '5'
            }
        }
        """

        config = cls.config()('config')
        text_part = pp.SkipTo(config | pp.StringEnd())('text')
        
        text_part.setParseAction(lambda t: [t[0].strip()])
        schema = text_part + pp.Optional(config)
        return schema

    @classmethod
    def parse_step_essay(cls, text: str) -> ParseResults:
        try:
            return cls.step_essay().parseString(text, parse_all=True).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
