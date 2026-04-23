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

from src.dump import BaseExporter


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
        # print(f'StepNumber.parse: {res=}')

        self.answer = [
            {
                'answer': str(float(item['number'])),
                'max_error': str(float(item.get('accuracy', 0)))
            }
            for item in res['answer']
        ]

        self.text = self.h2() + res['text']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        from copy import deepcopy
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        # реализовано для множественного ответа
        d['stepSource']['block']['source']['options'] = self.answer
        d['stepSource']['block']['source']['sample_size'] = len(self.answer)
        if 'score' in self.config:
            d['stepSource']['cost'] = self.config['score']

        return d


class ParseSchemaStepNumber(ParseSchema):
    @classmethod
    def answer(cls) -> pp.ParserElement:
        """Scheme 'ANSWER: 10.5 [+-0.1]' """
        keyword = pp.Keyword('ANSWER', caseless=True)
        number = cls.number
        accuracy = (pp.Suppress(pp.Literal('+-')) + cls.number)('accuracy')
        accuracy.set_parse_action(lambda t: t.as_list()[
            0] if isinstance(t, ParseResults) else t)
        schema = (pp.Suppress(pp.Combine(pp.LineStart() + keyword) + pp.one_of([":", "="]))
                  + number('answer')
                  + pp.Opt(accuracy))
        schema.set_parse_action(
            lambda t: {'number': t.answer.as_list()[0] if isinstance(t.answer, ParseResults) else t.answer,
                       'accuracy': t.accuracy or 0})
        return schema

    # @classmethod
    # def parse_answer(cls, line: str) -> (bool, int | float, int | float):
    #     """Разбор заголовка шага.'ANSWER: 10.5 [+-0.1]' to (ok, number, accuracy).
    #     По умолчанию accuracy=0
    #     """
    #     try:
    #         res = cls.answer().parse_string(line, parse_all=True).as_dict()
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
        {'text': ['Условие задачи.\nМного строк'], 'answer': [{'number': 3.14, 'accuracy': 0.1}], 'config': [{'score': '5'}]}
        """
        answer = cls.answer()
        config = cls.config()('config')
        answers = pp.OneOrMore(answer)('answer')
        sections = answers & pp.Opt(config)

        text_bound = cls.quoted() | sections
        text_part = pp.SkipTo(text_bound)
        # это не помогло починить пропажу \n перед началом quoted:
        # text_part.setWhitespaceChars(' \t\r')
        statement = (text_part + pp.ZeroOrMore(cls.quoted + text_part))("text")
        # без этого пропадает \n перед началом ```
        statement.set_parse_action(
            lambda t: '\n'.join(map(str.strip, t.as_list())))
        schema = statement + sections
        return schema

    @classmethod
    def parse_step_number(cls, text: str) -> ParseResults:
        try:
            return cls.step_number().parse_string(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)


class NumberDump(BaseExporter):
    """Обработка численных задач (NUMBER)"""

    def format_output(self) -> str:
        """
        Из
        {
          "block": {
            "name": "number",
            "text": "текст условия задачи в html",
            "source": {
              "options": [{
                  "answer": "4.0",
                  "max_error": "0.0"
                },
                {
                  "answer": "-8.5",
                  "max_error": "0.1"
                }],
            },
          },
        }
        возвращаем в виде строки
        текст условия задачи в markdown

        ANSWER: 4.0
        ANSWER: -8.5 +- 0.1

        :return: шаг в виде строки в формате markdown
        """

        source: dict[str, any] = self.block.get("source", {})
        options: list[dict[str, str]] = source.get("options", [])

        # Правильных ответов может быть несколько
        answers: list[str] = []
        for opt in options:
            answer: str = opt["answer"]
            max_error: str = opt.get("max_error", "0")

            try:
                if max_error and float(max_error) != 0:
                    answers.append(f"ANSWER: {answer} +-{max_error}")
                else:
                    answers.append(f"ANSWER: {answer}")
            except ValueError:
                raise ValueError(
                    f"WARNING: Некорректное значение max_error='{max_error}' для ответа '{answer}' в шаге {self.position}"
                )

        result_parts: list[str] = [
            self.html_to_markdown(self.soup),
            "",
            *answers,
            "",
            "CONFIG",
            *self.dump_config(source, self.step_data)
        ]
        return "\n".join(result_parts) + "\n"
