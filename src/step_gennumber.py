"""
Разбор шага типа GENNUMBER - численная задача со случайной генерацией условия.

https://stepik.org/lesson/385343/
{
    "block":{
        "name":"random-tasks",
        "text":"<p>Текст условия</p>",
        "video":null,
        "options":{},
        "subtitle_files":[],
        "is_deprecated":false,
        "source": {
            "task":"В саду цветут яблони и груши.\nПчела опылила \\x цветочков, а шмель \\y.\nСколько цветочков они опылили вместе? ",
            "solve":"x+y",
            "max_error":"0",
            "ranges":
            [
                {
                    "variable":"x",
                    "num_from":"1",
                    "num_to":"20",
                    "num_step":"1"
                },
                {
                    "variable":"y",
                    "num_from":"1",
                    "num_to":"15",
                    "num_step":"1"
                }
            ],
            "combinations":266
        }
        "subtitles":{},
        "tests_archive":null,
        "feedback_correct":"",
        "feedback_wrong":""
    },
    "id":"9939791",
    "has_review":false,
    "time":"2026-04-14T19:31:40.710Z"
}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepGennumber(Step):
    DEFAULT_SCORE = 1
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': '',
                'name': 'random-tasks',
                'source': {
                    'task': '', # текст задания
                    'solve': '', # формула решения
                    'max_error': '', # допустимая ошибка
                    'ranges': [], # список используемых переменных с их диапазоном
                    'combinations': 1 # число комбинаций
                }
            },
            'lesson': None,
            'position': None,
            'cost': DEFAULT_SCORE
        }
    }
    DEFAULT_RANGE = { # составная часть 'ranges' из DEFAULT_BODY, описание переменных
        'variable': '',
        'num_from': '',
        'num_to': '',
        'num_step': ''
    }

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepGennumber.parse_step_gennumber(text)
        print(f'StepGennumber.parse: {res=}')

        self.task = res['task']
        self.solve, self.max_error = self._extract_solve_and_max_error(res['answer'])
        self.ranges = res['ranges']

        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def _extract_solve_and_max_error(self, answer: str) -> tuple[str, float]:
        """Разделяет строку с ответом на выражение-ответ и погрешность"""
        # self.answer состоит из выражения-ответа +- погрешности(опционально)
        # причем stepik +- может воспринимать в ответе (как вычитание)
        # поэтому если есть +- берем последнее значение
        parts = answer.rsplit("+-", 1)

        # Если есть '+-', то проверяем, что второй элемент всё же число, а не часть ответа-выражения
        # (на stepik погрешность может быть задана только числом)
        if (len(parts) == 2):
            try:
                return parts[0].strip(), float(parts[1])
            except ValueError: # считает +- вычитанием в ответе
                return answer.strip(), 0
        else:
            return answer.strip(), 0

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)


        html_part, condition_part = (self.task).rsplit("CONDITION", 1)
        d['stepSource']['block']['text'] = markdown_to_html(html_part)
        d['stepSource']['block']['source']['task'] = condition_part

        
        d['stepSource']['block']['source']['solve'] = self.solve
        d['stepSource']['block']['source']['max_error'] = str(self.max_error)


        for var_range in self.ranges:
            r = deepcopy(self.DEFAULT_RANGE)
            r['variable'] = var_range['var']

            # обработка содержимого 'range': [1, 20, 1]

            if len(var_range['range']) == 1: # range(stop)
                r['num_from'] = 0
                r['num_to'] = var_range['range'][0]
                r['num_step'] = 1
            elif len(var_range['range']) == 2: # range(start, stop)
                r['num_from'] = var_range['range'][0]
                r['num_to'] = var_range['range'][1]
                r['num_step'] = 1
            else: # range(start, stop, step)
                r['num_from'] = var_range['range'][0]
                r['num_to'] = var_range['range'][1]
                r['num_step'] = var_range['range'][2]

            d['stepSource']['block']['source']['combinations'] *= (r['num_to'] - r['num_from']) // r['num_step']
            
            r['num_from'] = str(r['num_from'])
            r['num_to'] = str(r['num_to'])
            r['num_step'] = str(r['num_step'])

            d['stepSource']['block']['source']['ranges'].append(r)
            
        d['stepSource']['block']['source']['combinations'] = str(d['stepSource']['block']['source']['combinations'])


        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            else:
                # у этой задачи нет других опций
                option = self.config[key]
                d['stepSource']['block']['source']['options'][key] = ParseSchema.to_boolean(
                    option)
                
        print(f"{d = }")
        return d


class ParseSchemaStepGennumber(ParseSchema):
    @classmethod
    def step_gennumber(cls) -> pp.ParserElement:
        r"""
        text
        '''
        В саду цветут яблони и груши.
        Пчела опылила \x цветочков, а шмель \y.
        Сколько цветочков они опылили вместе?

        ANSWER 
        x+y

        VAR
        x (1, 20, 1)
        y (1, 15, 1)

        CONFIG
        score: 2
        '''
        to dict
        {
            'task': 'В саду цветут яблони и груши.\nПчела опылила \x цветочков, а шмель \y.\nСколько цветочков они опылили вместе?',
            'solve': '\nx+y\n',
            'ranges': 
            [
                {
                    'var': 'x', 
                    'range': [1, 20, 1]
                }, 
                {
                    'var': 'y', 
                    'range': [1, 15, 1]
                }
            ]
            'config': 
            {
                'score': '2'
            }
        }
        """
        # БЛОК VARS
        var_section_keyword = pp.LineStart() + "VAR"

        var_row = pp.Group(
             # stepik допускает любые комбинации из английских букв, цифр и _
             # (даже 4y_5 в качестве переменной)
            pp.Word(pp.alphanums + "_")('var')
            + pp.Suppress("(")
            + pp.Group(pp.DelimitedList(cls.number))('range')
            + pp.Suppress(")")
        )
        var_rows = var_section_keyword + pp.OneOrMore(var_row)('ranges')


        # БЛОК ANSWER
        answer_section_keyword = pp.LineStart() + "ANSWER"
        answer = answer_section_keyword + pp.SkipTo(var_rows)('answer')

        # ОБЪЕДИНЕНИЕ БЛОКОВ
        config = cls.config()('config')
        sections = answer & var_rows & pp.Opt(config)

        text_bound = cls.quoted() | sections
        task = pp.SkipTo(text_bound)("task")
        
        schema = task + sections
        return schema

    @classmethod
    def parse_step_gennumber(cls, text: str) -> ParseResults:
        try:
            print(text)
            return cls.step_gennumber().parse_string(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)


text = r'''
В саду цветут яблони и груши.
Пчела опылила \x цветочков, а шмель \y.
Сколько цветочков они опылили вместе?

ANSWER 
x+y

VAR
x (1, 20, 1)
y (1, 15, 1)

CONFIG
score: 2
'''
if __name__ == "__main__":
    import pprint
    res = ParseSchemaStepGennumber.parse_step_gennumber(text)
    pprint.pprint(res)