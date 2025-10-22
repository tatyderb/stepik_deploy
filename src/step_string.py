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
"""
{
    "block":
        {
        "name":"string",
        "text":"<p>стих</p>\n\n<p> </p>\n\n<p>Под голубыми небесамиВеликолепными коврами,Блестя на солнце, снег лежит;Прозрачный лес один чернеет,И ель сквозь иней зеленеет,И речка подо льдом блестит.<br>\n </p>",
        "video":null,
        "options":{},
        "subtitle_files":[],
        "is_deprecated":false,
        "source":{
            "pattern":"Под голубыми небесами\nВеликолепными коврами,\nБлестя на солнце, снег лежит;\nПрозрачный лес один чернеет,\nИ ель сквозь иней зеленеет,\nИ речка подо льдом блестит.\n",
            "use_re":false,
            "match_substring":false,
            "case_sensitive":false,
            "code":"# def check(reply):\n#     \"\"\"Evaluate the learner's reply.\n#\n#     It should return 1 or True for the correct reply and 0 or False\n#     for the incorrect one.\n#\n#     A partial solution may be scored using a float number from the\n#     interval (0, 1). In such a case the learner total score for the\n#     problem will be 'step cost' * 'score'.\n#\n#     :param reply: a string that is the learner's reply to the problem\n#     :return: a score number (int or float) in range [0, 1]\n#\n#     \"\"\"\n#     return reply == \"Hello\"\n\n# def solve():\n#     \"\"\"Return a correct reply. This function is *optional*.\n#\n#     It is used to test the correctness of the 'check' function.\n#\n#     :return: a string that is a correct reply to the problem\n#\n#     \"\"\"\n#     return \"Hello\"",
            "is_text_disabled":false,
            "is_file_disabled":true
        },
        "subtitles":{},
        "tests_archive":null,
        "feedback_correct":"",
        "feedback_wrong":""
    },
    "id":"8461521",
    "has_review":false,
    "time":"2025-10-18T18:39:19.547Z"
}

"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepString(Step):
    DEFAULT_SCORE = 1
    DEFAULT_BODY = {
        'stepSource': {
            "block": {
                "name": "string",
                "text": "Вы можете изменить условие задания в этом поле и указать настройки ниже.",
                "video": None,
                "options": {},
                "source": {
                    "pattern": "Ответ / регулярное выражение в качестве ответа",
                    "use_re": False,
                    "match_substring": False,
                    "case_sensitive": False,
                    "code": "# def check(reply):\n#     \"\"\"Evaluate the learner's reply.\n#\n#     It should return 1 or True for the correct reply and 0 or False\n#     for the incorrect one.\n#\n#     A partial solution may be scored using a float number from the\n#     interval (0, 1). In such a case the learner total score for the\n#     problem will be 'step cost' * 'score'.\n#\n#     :param reply: a string that is the learner's reply to the problem\n#     :return: a score number (int or float) in range [0, 1]\n#\n#     \"\"\"\n#     return reply == \"Hello\"\n\n# def solve():\n#     \"\"\"Return a correct reply. This function is *optional*.\n#\n#     It is used to test the correctness of the 'check' function.\n#\n#     :return: a string that is a correct reply to the problem\n#\n#     \"\"\"\n#     return \"Hello\"",
                    "is_text_disabled": False,
                    "is_file_disabled": True
                },
                "subtitles":{},
                "tests_archive":None,
                "feedback_correct":"",
                "feedback_wrong":""
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
        res = ParseSchemaStepString.parse_step_string(text)
        print(f'StepString.parse: {res=}')

        self.text = res['text']
        markdown_text = '## ' + self.header + '\n' + self.text
        self.text = markdown_text
        self.answer = res['answer']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        d['stepSource']['block']['source']['pattern'] = self.answer
        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            else:
                option = self.config[key]
                d['stepSource']['block']['source'][key] = ParseSchema.to_boolean(option)
        return d


class ParseSchemaStepString(ParseSchema):
    @classmethod
    def answer(cls) -> pp.ParserElement:
        """Schema 'ANSWER: регулярное выражение'
         Пробелы или переносы строк перед текстом удаляются """
        keyword = pp.Keyword('ANSWER', caseless=True)
        answer = pp.SkipTo(pp.CaselessKeyword('ANSWER') | pp.CaselessKeyword('CONFIG') | pp.StringEnd())
        
        schema = pp.Suppress(pp.Combine(pp.LineStart() + keyword) + pp.oneOf([":", "="])) + \
            pp.Optional(pp.White(' ')) + pp.Optional(pp.LineEnd()) + answer()('answer') 
        schema.setParseAction(
            lambda t: t.answer[0])
        return schema

    @classmethod
    def step_string(cls) -> pp.ParserElement:
        """
        text
        Условие задачи.
        ANSWER строка/регулярное выражение/много строк
        CONFIG
        score: 5
        to dict
        {
            'text': 'Условие задачи.',
            "pattern":"строка/регулярное выражение/много строк",
            "use_re": False,
            "match_substring": False,
            "case_sensitive": False,
            "code":"# def check(reply):\n#     \"\"\"Evaluate the learner's reply.\n#\n#     It should return 1 or True for the correct reply and 0 or False\n#     for the incorrect one.\n#\n#     A partial solution may be scored using a float number from the\n#     interval (0, 1). In such a case the learner total score for the\n#     problem will be 'step cost' * 'score'.\n#\n#     :param reply: a string that is the learner's reply to the problem\n#     :return: a score number (int or float) in range [0, 1]\n#\n#     \"\"\"\n#     return reply == \"Hello\"\n\n# def solve():\n#     \"\"\"Return a correct reply. This function is *optional*.\n#\n#     It is used to test the correctness of the 'check' function.\n#\n#     :return: a string that is a correct reply to the problem\n#\n#     \"\"\"\n#     return \"Hello\"",
            "is_text_disabled": False,
            "is_file_disabled": True
        }
        """

        answer = cls.answer()
        answers = pp.OneOrMore(answer)('answer')
        config = cls.config()('config')

        sections = answers & pp.Opt(config)

        text_bound = cls.quoted() | sections
        text_part = pp.SkipTo(text_bound)

        text_part = pp.SkipTo(pp.CaselessKeyword('ANSWER'))('text')
        text_part.setParseAction(lambda t: t[0].strip())
        
        schema = text_part + sections

        return schema

    @classmethod
    def parse_step_string(cls, text: str) -> ParseResults:
        try:
            res = cls.step_string().parseString(text, parse_all=True).as_dict()
            if len(res['answer']) == 1:
                res['answer'] = res['answer'][0]
            else: # если было несколько ANSWER, создаем регулярное выражение
                if 'config' not in res:
                    res['config'] = {}
                res['config']['use_re'] = 'true'
                res['answer'] = '|'.join(res['answer'])
            return res
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
