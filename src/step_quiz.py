"""
Разбор шага типа QUIZ - выбор одного или выбор нескольких вариантов из списка.

https://stepik.org/lesson/385334/step/1
{
    "block": {
        "name": "choice",
        "text": "<h2>Выбор одного</h2>\n<p>Выберите один правильный ответ.</p>\n<p>2 + 3 = ?</p>",
        "video": null,
        "options": {
            "is_multiple_choice": false
        },
        "subtitle_files": [],
        "is_deprecated": false,
        "source": {
            "options": [
                {
                    "is_correct": true,
                    "text": "<p>5</p>",
                    "feedback": ""
                },
                {
                    "is_correct": false,
                    "text": "<p>-5</p>",
                    "feedback": ""
                },
                {
                    "is_correct": false,
                    "text": "<p>0</p>",
                    "feedback": ""
                },
                {
                    "is_correct": false,
                    "text": "<p>55</p>",
                    "feedback": ""
                }
            ],
            "is_always_correct": false,
            "is_html_enabled": true,
            "sample_size": 4,
            "is_multiple_choice": false,
            "preserve_order": false,
            "is_options_feedback": false
        },
        "subtitles": {},
        "tests_archive": null,
        "feedback_correct": "",
        "feedback_wrong": ""
    },
    "id": "1942435",
    "has_review": false,
    "time": "2025-09-23T12:55:07.121Z"
}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html


class StepQuiz(Step):
    DEFAULT_SCORE = 2
    DATA_TEMPLATE = {
        'stepSource': {
            'block': {
                'name': 'choice',
                'text': 'Pick one!',  # question text in html
                'source': {
                    'options': [],  # add answer variants here, use option_template
                    'is_always_correct': False,
                    'is_html_enabled': True,
                    'sample_size': 0,  # len of 'options' list
                    'is_multiple_choice': False,
                    'preserve_order': False,
                    'is_options_feedback': False  # https://github.com/StepicOrg/Stepik-API/issues/67
                }
            },
            'lesson': None,
            'position': None,
            'cost': DEFAULT_SCORE
        }
    }
    OPTION_TEMPLATE = {'is_correct': False, 'text': '2+2=3', 'feedback': ''}

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepQuiz.parse_step_quiz(text)
        # {'text': 'Условие',
        # 'variants': [{'letter': 'A', 'text': ' variant1'}, {'letter': 'B', 'text': ' variant2'}, {'letter': 'C', 'text': ' variant 3'}],
        # 'answer': ['A', 'C'],
        #  'config': [{'shuffle': 'false'}]}
        print(f'StepQuiz.parse: {res=}')

        self.options = [
            {'is_correct': d['letter'] in res['answer'], 'text': markdown_to_html(d['text']), 'feedback': ''}
            for d in res['variants']
        ]
        self.is_multiple_choice = len(res['answer']) > 1

        self.config = res.get('config', {})

        self.text = res['text']
        markdown_text = '## ' + self.header + '\n' + self.text
        self.text = markdown_text

    def to_dict(self) -> dict:
        from copy import deepcopy
        d = deepcopy(self.DATA_TEMPLATE)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        # один ответ
        d['stepSource']['block']['source']['options'] = self.options
        d['stepSource']['block']['source']['sample_size'] = len(self.options)
        d['stepSource']['block']['source']['is_multiple_choice'] = self.is_multiple_choice
        d['stepSource']['block']['source']['preserve_order'] = bool(self.config.get('shuffle', False))

        d['stepSource']['score'] = self.config.get('score', self.DEFAULT_SCORE)

        return d

class ParseSchemaStepQuiz(ParseSchema):
    @classmethod
    def answer(cls) -> pp.ParserElement:
        """Scheme 'ANSWER: A, C' """
        keyword = pp.Keyword('ANSWER', caseless=True)
        letter = pp.Word(pp.alphas, exact=1)
        letters = (letter + pp.ZeroOrMore(pp.Suppress(',') + letter))('letters')
        schema = pp.Suppress(pp.Combine(pp.LineStart() + keyword) + ':') + letters
        schema.setParseAction(lambda t: t.letters)
        return schema

    @classmethod
    def step_quiz(cls) -> pp.ParserElement:
        """
        text
        A. variant1
        B. variant2
        C. variant3
        ANSWER: A, C
        CONFIG:
        shuffle: false
        to dict
        {
            'text': ['Условие задачи.\nМного строк'],
            'variants': ['variant1', 'variant2', 'variant3'],
            'answer': ['A', 'C'],
            'config': [{'shuffle': False}]
        }
        """
        answer = cls.answer()('answer')
        config = cls.config()('config')

        # A. variant1
        letter = pp.Word(pp.alphas, exact=1)
        variant_letter = pp.Combine(pp.LineStart() + letter + pp.Suppress('.'))('letter')
        variant_text = pp.SkipTo(variant_letter | answer | config)('text')
        variant = variant_letter + variant_text
        variant.setParseAction(lambda t: {'letter': t.letter, 'text': t.text})

        # условие - все до первого варианта ответа
        text_bound = cls.quoted() | variant
        text_part = pp.SkipTo(text_bound)
        # это не помогло починить пропажу \n перед началом quoted:
        statement = (text_part + pp.ZeroOrMore(cls.quoted + text_part))("text")
        # без этого пропадает \n перед началом ```
        statement.setParseAction(lambda t: '\n'.join(map(str.strip, t.as_list())))
        schema = statement + pp.OneOrMore(variant)('variants') + answer + pp.Opt(config)
        return schema

    @classmethod
    def parse_step_quiz(cls, text: str) -> ParseResults:
        try:
            return cls.step_quiz().parseString(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)

