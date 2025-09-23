"""
Разбор шага типа NUMBER - ввод числа.

https://stepik.org/lesson/308220/step/9
{
    "block": {
        "name": "number",
        "text": "<h2>Ответ - число</h2>\n<p>Напишите ответ.</p>\n<p>2 + 5 = ?</p>",
        "video": null,
        "options": {},
        "subtitle_files": [],
        "is_deprecated": false,
        "source": {
            "options": [
                {
                    "answer": "7.0",
                    "max_error": "0"
                }
            ],
            "sample_size": 1,
            "is_options_feedback": false
        },
        "subtitles": {},
        "tests_archive": null,
        "feedback_correct": "",
        "feedback_wrong": ""
    },
    "id": "3241278",
    "has_review": false,
    "time": "2025-09-21T10:40:08.931Z"
}

"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html


class StepNumber(Step):
    DEFAULT_SCORE = 2
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'name': 'number',
                'text': 'Enter the answer',  # task text in html
                'source': {
                    'options': [],  # add answer variants here, use option_template
                    'sample_size': 0,  # len of 'options' list
                    'is_options_feedback': False
                }
            },
            'lesson': None,
            'position': None,
            'cost': DEFAULT_SCORE
        }
    }
    OPTION_TEMPLATE = {'answer': '4', 'max_error': '0'}

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepNumber.parse_step_number(text)
        print(f'StepNumber.parse: {res=}')

        self.answer = dict()
        answer = res['answer']
        self.answer['answer'] = str(float(answer['number']))
        self.answer['max_error']  = str(float(answer.get('accuracy', 0)))

        self.text = res['text']
        markdown_text = '## ' + self.header + '\n' + self.text
        self.text = markdown_text

    def to_dict(self) -> dict:
        d = self.DEFAULT_BODY.copy()
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        # один ответ
        d['stepSource']['block']['source']['options'] = [self.answer]
        d['stepSource']['block']['source']['sample_size'] = 1

        return d

class ParseSchemaStepNumber(ParseSchema):
    @classmethod
    def answer(cls) -> pp.ParserElement:
        """Scheme 'ANSWER: 10.5 [+-0.1]' """
        keyword = pp.Keyword('ANSWER', caseless=True)
        number = cls.number
        accuracy = (pp.Suppress(pp.Literal('+-')) + cls.number)('accuracy')
        accuracy.setParseAction(lambda t: t.as_list()[0] if isinstance(t, ParseResults) else t)
        schema = pp.Suppress(pp.Combine(pp.LineStart() + keyword) + ':') + number('answer') + pp.Opt(accuracy)
        schema.setParseAction(
            lambda t: {'number': t.answer.as_list()[0] if isinstance(t.answer, ParseResults) else t.answer,
                 'accuracy': t.accuracy or 0})
        return schema

    # @classmethod
    # def parse_answer(cls, line: str) -> (bool, int | float, int | float):
    #     """Разбор заголовка шага.'ANSWER: 10.5 [+-0.1]' to (ok, number, accuracy).
    #     По умолчанию accuracy=0
    #     """
    #     try:
    #         res = cls.answer().parseString(line, parse_all=True).as_dict()
    #         print(f'\nparse_answer: {res=}')
    #         number = res['answer']
    #         accuracy = res['accuracy'][0] if 'accuracy' in res else 0
    #         return True, number, accuracy
    #     except pp.ParseException:
    #         return False, 0, 0

    @classmethod
    def step_number(cls) -> pp.ParserElement:
        """
        text
        ANSWER: number +-accuracy
        to dict
        {'text': ['Условие задачи.\nМного строк'], 'answer': {'number': 3.14, 'accuracy': 0.1}, 'config': [{'score': '5'}]}
        """
        answer = cls.answer()('answer')
        config = cls.config()('config')
        sections = (answer & pp.Opt(config))

        text_bound = cls.quoted() | sections
        text_part = pp.SkipTo(text_bound)
        # это не помогло починить пропажу \n перед началом quoted:
        # text_part.setWhitespaceChars(' \t\r')
        statement = (text_part + pp.ZeroOrMore(cls.quoted + text_part))("text")
        # без этого пропадает \n перед началом ```
        statement.setParseAction(lambda t: '\n'.join(map(str.strip, t.as_list())))
        schema = statement + sections
        return schema

    @classmethod
    def parse_step_number(cls, text: str) -> ParseResults:
        try:
            return cls.step_number().parseString(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)

