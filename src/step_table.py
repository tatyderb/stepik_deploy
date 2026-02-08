"""
Разбор шага типа TABLE - табличная задача.

https://stepik.org/lesson/385337
{
    "block":{
        "name":"table",
        "text":"<p>Текст условия</p>",
        "video":null,
        "options":{},
        "subtitle_files":[],
        "is_deprecated":false,
        "source":{
            "rows":[
                {
                    "name":"Первый ряд",
                    "columns":[{"choice":true},{"choice":false}]
                },
                {
                    "name":"Второй ряд",
                    "columns":[{"choice":false},{"choice":true}]
                }
            ],
            "options":{
                "is_checkbox":false,
                "is_randomize_rows":true,
                "is_randomize_columns":true,
                "sample_size":-1
            },
            "columns":[
                {"name":"Первая колонка"},
                {"name":"Вторая колонка"}
            ],
            "description":"Ряды: ",
            "is_always_correct":false
        },
        "subtitles":{},
        "tests_archive":null,
        "feedback_correct":"",
        "feedback_wrong":""
    },
    "id":"9485455",
    "has_review":false,
    "time":"2026-02-07T10:04:48.915Z"
}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html
from copy import deepcopy


class StepTable(Step):
    DEFAULT_SCORE = 1
    DEFAULT_BODY = {
        'stepSource': {
            'block': {
                'text': 'Условие задачи',
                'name': 'table',
                'source': {
                    "rows": [],     # основные строки таблицы
                    'options':  {
                        'is_checkbox': False,
                        'is_randomize_rows': True,
                        'is_randomize_columns': True,
                        'sample_size': -1
                    },
                    'columns': [],  # названия колонок
                    'description': 'Ряды: ',  # название первой колонки
                    'is_always_correct': False
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
        res = ParseSchemaStepTable.parse_step_table(text)
        print(f'StepTable.parse: {res=}')

        self.text = self.h2() + res['text']
        self.table_rows = res['table_rows']
        self.config = {}
        if 'config' in res:
            self.config = res['config']

    def to_dict(self) -> dict:
        d = deepcopy(self.DEFAULT_BODY)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)

        # обработка строк таблицы
        d['stepSource']['block']['source']['description'] = self.table_rows[0][0]
        columns_data = []
        for column_name in self.table_rows[0][1:]:
            column_dict = {
                "name": column_name
            }
            columns_data.append(column_dict)

        d['stepSource']['block']['source']['columns'] = columns_data

        for row in self.table_rows[1::]:
            if all(cell.replace("-", "") == "" for cell in row):
                continue
            print(row)
            for i in range(1, len(row)):
                row[i] = ParseSchema.to_boolean(row[i])

            row_dict = {
                "name": row[0],
                "columns": []
            }

            for i in range(1, len(row)):
                column_dict = {
                    "choice": row[i]
                }
                row_dict["columns"].append(column_dict)

            d['stepSource']['block']['source']['rows'].append(row_dict)

        for key in self.config:
            if key == 'score':
                d['stepSource']['cost'] = self.config['score']
            elif key == 'is_always_correct':
                option = self.config[key]
                d['stepSource']['block']['source']['is_always_correct'] = ParseSchema.to_boolean(
                    option)
            else:
                option = self.config[key]
                d['stepSource']['block']['source']['options'][key] = ParseSchema.to_boolean(
                    option)
        return d


class ParseSchemaStepTable(ParseSchema):
    @classmethod
    def step_table(cls) -> pp.ParserElement:

        config = cls.config()('config')

        keyword = pp.LineStart() + "TABLE"
        description = pp.SkipTo(keyword).setParseAction(
            lambda t: t[0].strip())("text")

        table_row = pp.Group(
            pp.Suppress("|")
            + pp.DelimitedList(pp.CharsNotIn("|\n").setParseAction(lambda t: t[0].strip()), delim="|")
            + pp.Suppress("|")
        )

        schema = (
            pp.Optional(description) +
            keyword +
            pp.ZeroOrMore(table_row)('table_rows') +
            pp.Optional(config))
        return schema

    @classmethod
    def parse_step_table(cls, text: str) -> ParseResults:
        try:
            return cls.step_table().parseString(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)
