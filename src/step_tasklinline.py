"""
Разбор шага типа TASKINLINE - выбор одного или выбор нескольких вариантов из списка.

https://stepik.org/lesson/59057/step/1
"source"]["code"] = содержимое вкладки, где определены check :
"code_templates": {
    "c": ""
},
"code_templates_header_lines_count": {
    "c": 15
},
"code_templates_footer_lines_count": {
    "c": 0
},
"code_templates_options": {},




Код json блока не подходит для отправки как есть, надо править.
{
    "stepSource": {
        "reason_of_failure": "",
        "error": {
            "text": "",
            "code": "",
            "params": {}
        },
        "warnings": [],
        "instruction_id": null,
        "has_instruction": false,
        "cost": 10,
        "is_solutions_unlocked": false,
        "solutions_unlocked_attempts": 3,
        "max_submissions_count": 3,
        "has_submissions_restrictions": false,
        "create_date": "2020-09-20T19:50:33.000Z",
        "actions": {
            "edit_instructions": "#",
            "submit": "#"
        },
        "block": {
            "name": "code",
            "text": "<p>Даны координаты 3 вершин треугольника (x1, y1), (x2, y2), (x3, y3).</p>\n<p><strong>Возьмите функцию</strong> <code>dist(x1, y1, x2, y2)</code>, которая вычисляет расстояние между ними по формуле $$c^2 = (x_1 - x_2)^2 + (y_1 - y_2)^2$$ из предыдущей задачи.</p>\n<p><strong>Напишите функцию</strong> <code>area(x1, y1, x2, y2, x3, y3)</code>, которая вычисляет площадь треугольника со сторонами $a, b, c$ по формуле $$s = \\sqrt {p \\cdot (p - a) \\cdot (p - b) \\cdot (p-c)}$$, где $p = (a + b + c) / 2$</p>\n<p><img src=\"http://judge2.vdi.mipt.ru/tasks/func/geron.jpg\" width=\"300\"></p>\n<pre><code class=\"python\">from math import sqrt  # функция вычисляет квадратный корень\n\ndef dist(x1, y1, x2, y2):\n# скопируйте код из предыдущей задачи\n\ndef area(x1, y1, x2, y2, x3, y3):\n# тут нужно написать код\n\nx1, y1, x2, y2, x3, y3 = map(float, input().split())\ns = area(x1, y1, x2, y2, x3, y3)\nprint(s)\n</code></pre>",
            "video": null,
            "options": {
                "execution_time_limit": 5,
                "execution_memory_limit": 256,
                "limits": {
                    "python3": {
                        "time": 15,
                        "memory": 256
                    }
                },
                "code_templates": {
                    "python3": "from math import sqrt\n\ndef dist(x1, y1, x2, y2):\n    dx = x1 - x2\n    dy = y1 - y2\n    return sqrt(dx*dx + dy*dy)\n\ndef area(x1, y1, x2, y2, x3,y3):\n    # тут нужно написать код, воспользуйтесь функцией dist\n\nx1, y1, x2, y2, x3,y3 = map(float, input().split())\ns = area(x1, y1, x2, y2, x3,y3)\nprint(s)"
                },
                "code_templates_header_lines_count": {
                    "python3": 0
                },
                "code_templates_footer_lines_count": {
                    "python3": 0
                },
                "code_templates_options": {},
                "samples": [
                    [
                        "3 0 0 4 0 0",
                        "6.0"
                    ]
                ],
                "is_run_user_code_allowed": true
            },
            "subtitle_files": [],
            "source": {
                "code": "# This is a sample Code Challenge\n# Learn more: https://stepik.org/lesson/9173\n# Ask your questions via support@stepik.org\n\nimport math\n\ndef generate():\n    return [] \n\ndef check(reply, clue):\n    if reply == '':\n        return False\n    reply = float(reply)\n    clue = float(clue)\n    return abs(float(reply) - float(clue)) < 0.01\n    #return reply.strip() == clue.strip()\n\ndef dist(x1, y1, x2, y2):\n    dx = x1 - x2\n    dy = y1 - y2\n    return math.sqrt(dx*dx + dy*dy)\n    \n#def solve(dataset):\n#    x1, y1, x2, y2, x3, y3 = map(float, dataset.split())\n#    a = dist(x1, y1, x2, y2)\n#    b = dist(x1, y1, x3, y3)\n#    c = dist(x2, y2, x3, y3)\n#    p = (a + b + c) / 2\n#    return str(math.sqrt(p*(p-a)*(p-b)*(p-c)))",
                "execution_memory_limit": 256,
                "execution_time_limit": 5,
                "is_memory_limit_scaled": true,
                "is_run_user_code_allowed": true,
                "is_time_limit_scaled": true,
                "manual_memory_limits": [],
                "manual_time_limits": [],
                "samples_count": 1,
                "templates_data": "::python3\nfrom math import sqrt\n\ndef dist(x1, y1, x2, y2):\n    dx = x1 - x2\n    dy = y1 - y2\n    return sqrt(dx*dx + dy*dy)\n        \ndef area(x1, y1, x2, y2, x3,y3):\n    # тут нужно написать код, воспользуйтесь функцией dist\n    \nx1, y1, x2, y2, x3,y3 = map(float, input().split())\ns = area(x1, y1, x2, y2, x3,y3)\nprint(s)\n    \n\n\n\n\n",
                "test_archive": [],
                "test_cases": [
                    [
                        "3 0 0 4 0 0",
                        "6.0"
                    ],
                    [
                        "0 4 3 0 0 0",
                        "6.0"
                    ],
                    [
                        "0 1 0 5 1 2",
                        "1.9999999999999991"
                    ],
                    [
                        "1 2 3 4 5 6",
                        "0.0"
                    ],
                    [
                        "-1.3 5.1 1.7 1.1 1.7 5.1",
                        "6.000000000000001"
                    ]
                ],
                "are_all_tests_scored": false
            },
            "subtitles": {},
            "tests_archive": "/api/step-sources/1576649/tests",
            "feedback_correct": "",
            "feedback_wrong": ""
        },
        "instruction_type": null,
        "lesson_id": "408292",
        "position": 6,
        "status": "ready",
        "instruction": null,
        "lesson": "408292"
    }
}
"""

import pyparsing as pp
from pyparsing import ParseResults

from src.checker import stepik_genchecksolve, get_checker_function_by_name, custom_genchecksolve
from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html

# https://stepik.org/lesson/59057/step/9
LANG_LIMITS = {
    "all": {
        "time": 5,
        "memory": 256
    },
    "c": {
        "time": 5,
        "memory": 256
    },
    "c_valgrind": {
        "time": 5,
        "memory": 256
    },
    "python3": {
        "time": 15,
        "memory": 256
    },
    "python3.10": {
        "time": 15,
        "memory": 256
    },
    "python3.12": {
        "time": 15,
        "memory": 256
    },

}


class StepTaskinline(Step):
    DEFAULT_SCORE = 10
    DEFAULT_LANG = 'all'
    DEFAULT_CHECKER_NAME = 'check_asis'
    DEFAULT_MODE = 'stepik'
    LANG_TEMPLATE = '::{lang}\n'
    CODE_TEMPLATE = '::code\n{code}\n'
    HEADER_TEMPLATE = '::header\n{header}\n'
    FOOTER_TEMPLATE = '::footer\n{footer}\n'
    TEST_EXAMPLE_SECTION_TEMPLATE = '<details><summary>Тестовые данные</summary>\n{}</details>'
    TEST_EXAMPLE_TEMPLATE = """
<h4>Test #{number} input</h4>
<pre>{test_input}</pre>
<h4>Test #{number} output</h4>
<pre>{test_output}</pre>
"""
    TEST_CLOSED = '<p>Остальные тесты закрыты авторами курса.</p>\n'


    # кроме заполнения темплит, нужно еще посчитать количество строк после ключевого слова
#     DATA_TEMPLATE = {
#     "stepSource": {
#         "reason_of_failure": "",
#         "error": {
#             "text": "",
#             "code": "",
#             "params": {}
#         },
#         "warnings": [],
#         "instruction_id": None,
#         "has_instruction": False,
#         "cost": DEFAULT_SCORE,
#         "is_solutions_unlocked": False,
#         "solutions_unlocked_attempts": 3,
#         "max_submissions_count": 3,
#         "has_submissions_restrictions": False,
#         "actions": {
#             "edit_instructions": "#",
#             "submit": "#"
#         },
#         "block": {
#             "name": "code",
#             "text": "",  # условие задачи
#             "video": None,
#             "options": {    # stepSource.block.options -ограничения на время и память, почему дублируется???
#                 "execution_time_limit": 5,
#                 "execution_memory_limit": 256,
#                 "limits": {
#                     "python3": {
#                         "time": 15,
#                         "memory": 256
#                     }
#                 },
#                 "code_templates": {
#                     "python3": ""  # stepSource.block.options.code_templates тут вставка шаблона для ученика, куда он будет всписывать код, секция CODE
#                 },
#                 "code_templates_header_lines_count": {
#                     "python3": 0   # от метки ::header до конца, не считая метки сколько линий
#                 },
#                 "code_templates_footer_lines_count": {
#                     "python3": 0
#                 },
#                 "code_templates_options": {},
#                 "samples": [     # сюда первый тест записать
#                     [
#                         "3 0 0 4 0 0",
#                         "6.0"
#                     ]
#                 ],
#                 "is_run_user_code_allowed": True
#             },
#             "subtitle_files": [],
#             "source": {
#                 "code": "", # содержимое последней вкладки: check, solve, generate
#                 "execution_memory_limit": 256,   # еще одни лимиты....
#                 "execution_time_limit": 5,
#                 "is_memory_limit_scaled": True,
#                 "is_run_user_code_allowed": True,
#                 "is_time_limit_scaled": True,
#                 "manual_memory_limits": [],
#                 "manual_time_limits": [],
#                 "samples_count": 1,       # сколько надо выводить примеров, оставляем 1
#                 "templates_data": "",  # содержимое второй вкладки Языки и шаблоны, всей (видимо)
#                 "test_archive": [],
#                 "test_cases": [],    # список тестов, [["input1", "output1"], ["input2", "output2"]]
#                 "are_all_tests_scored": False
#             },
#             "subtitles": {},
#             "tests_archive": "/api/step-sources/1576649/tests",    # id шага
#             "feedback_correct": "",
#             "feedback_wrong": ""
#         },
#         "instruction_type": None,
#         "lesson_id": "408292",    # id урока
#         "position": 6,            # позиция шага от 1
#         "status": "ready",
#         "instruction": None,
#         "lesson": "408292"       # id урока
#     }
# }
    DATA_TEMPLATE = {
    "stepSource": {
        "reason_of_failure": None,
        "instruction_id": None,
        "has_instruction": False,
        "cost": DEFAULT_SCORE,
        "is_solutions_unlocked": True,
        "solutions_unlocked_attempts": 4,
        "max_submissions_count": 3,
        "has_submissions_restrictions": False,
        "create_date": None,
        "block": {
            "text": "<p>Вы можете изменить условие задания в этом поле и указать настройки ниже.<br />\n<br />\nНапишите функцию <code>int sum(int a, int b)</code>, которая считает сумму двух чисел.</p>",
            "name": "code",
            "video": None,
            "options": None,
            "source": {
                "code": "# This is a sample Code Challenge\n# Learn more: https://stepik.org/lesson/9172\n# Ask your questions via help@stepik.org\n\ndef generate():\n    return []\n\ndef check(reply, clue):\n    return reply.strip() == clue.strip()\n\n# def solve(dataset):\n#     a, b = dataset.split()\n#     return str(int(a) + int(b))",
                "execution_time_limit": 5,
                "execution_memory_limit": 256,
                "samples_count": 1,
                "templates_data": "",  # все содержимое вкладки Языки и Шаблоны одной строкой.
                "is_time_limit_scaled": True,
                "is_memory_limit_scaled": True,
                "is_run_user_code_allowed": True,
                "manual_time_limits": [
                    {
                        "language": "c++",
                        "time": 7
                    },
                    {
                        "language": "c++11",
                        "time": 8
                    }
                ],
                "manual_memory_limits": [
                    {
                        "language": "c++",
                        "memory": 261
                    },
                    {
                        "language": "c++11",
                        "memory": 262
                    }
                ],
                "test_archive": [],
                "test_cases": [
                    [
                        "8 11\n",
                        "19\n"
                    ],
                    [
                        "2 3",
                        "5"
                    ]
                ]
            },
            "feedback_correct": "", # '"Это комментарий к верному ответу.",
            "feedback_wrong": "", # "Это комментарий к неверному ответу."
        },
        "instruction_type": None,
        "lesson_id": None,
        "position": 2,
        "status": "ready",
        "is_enabled": True,
        "needs_plan": None,
        "instruction": None,
        "lesson": "1950070"
    }
}

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)
        self.lang = self.DEFAULT_LANG
        self.tests = []         # список тестов в формате [['in1', 'out1'], ['in2', 'out2']]
        self.part_before = ''   # код, вставляемый до студенческого, секция HEADER и часть после ::header
        self.part_after = ''    # код, вставляемый после студенческого, секция FOOTER и часть после ::footer
        self.code = ''          # код, который показывается студенту в онлайн-редакторе, когда он переходит на задачу
        self.checker = self.DEFAULT_CHECKER_NAME
        self.additional_parameter = ''  # дополнительные параметры для чекера
        self.mode = self.DEFAULT_MODE   # 'stepik', 'custom' - как показывать тестовые данные и результаты тестирования
        self.open_tests = -1     # количество открытых тестов, -1 - все тесты открыты

        # нужно, чтобы полностью задать содержимое вкладок
        self.template = ''      # содержимое вкладки Языки и Шаблоны, вместо набора self.header, self.footer, self.code,
        self.generate_check_solve_tab = '' # содержимое вкладки Расширенный редактор

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepTaskinline.parse_step_testinline(text)
        # res={'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
        # 'tests': ['2 3', '5', '-17 -23', '-40'],
        # 'header': '#include <stdio.h>\nint module(int x);',
        # 'footer': 'int main()\n{\n    int x;\n    scanf("%d", &x);\n    printf("%d\n", module(x));\n    return 0;\n}',
        # 'code': 'int module(int x) {\n    // здесь нужно написать код\n}',
        # 'config': [{'lang': 'c'}]}
        # print(f'\nStepTaskinline.parse: {res=}')

        input_data = res['tests'][::2]
        output_data = res['tests'][1::2]
        self.tests = list(zip(input_data, output_data))

        self.config = res.get('config', {})
        if self.config.get('lang'):
            self.lang = self.config['lang']
        self.mode = self.config.get('mode', 'stepik')
        # -1 - все тесты открыты
        self.open_tests = int(self.config.get('open_tests', -1))
        if self.open_tests < 0 or self.open_tests > len(self.tests):
            self.open_tests = len(self.tests)
        # print(f'{self.open_tests=}')

        self.part_before = res.get('header', '')
        self.part_after = res.get('footer', '')
        self.code = res.get('code', '')
        self.template = res.get('template', '')
        self.generate_check_solve_tab = res.get('gencheksolve', '')

        # пока чекер по умолчанию от Степика
        self.checker = self.config.get('checker', self.DEFAULT_CHECKER_NAME)

        self.text = res['text']
        markdown_text = '## ' + self.header + '\n' + self.text
        self.text = markdown_text

    def to_dict(self) -> dict:
        from copy import deepcopy
        d = deepcopy(self.DATA_TEMPLATE)
        # при self.mode == 'custom' добавится раздел с тестовыми данными, см. ниже

        # лимиты на память и время размазаны по разным местам
        limits = LANG_LIMITS[self.lang]
        d['stepSource']['block']['source']['execution_time_limit'] = limits['time']
        d['stepSource']['block']['source']['execution_memory_limit'] = limits['memory']
        d['stepSource']['block']['source']["manual_memory_limits"] = []
        d['stepSource']['block']['source']["manual_time_limits"] = []

        d['stepSource']['block']['source']['templates_data'] = self.templates_data()

        # Представление тестовых данных и реакция на запуск программы определяется
        # self.mode == 'stepik'
        # * все тестовые данные заданы в d['stepSource']['block']['source']['test_cases']
        # * открытые и закрытые тесты регулируются силами Stepik через d['stepSource']['block']['source']['samples_count']
        # self.mode == 'custom'
        # * samples = 0,
        # * показ тестовых данных в условии; первый тест развернут, остальные под <details>
        # * результата прогонов регулируется через generate + check

        function = get_checker_function_by_name(self.checker)

        match self.mode:
            case 'stepik':
                # используем функциональность степика
                # содержимое последней вкладки с generate, check, solve
                # print('Генерируем данные для mode=stepik')
                d['stepSource']['block']['source']['code'] = \
                    self.generate_check_solve_tab or \
                    stepik_genchecksolve(checker_function=function, additional_parameter=self.additional_parameter)
                # тесты
                d['stepSource']['block']['source']['test_cases'] = self.tests
                d['stepSource']['block']['source']['samples_count'] = self.open_tests

            case 'custom':
                # используем функциональность степика
                # содержимое последней вкладки с generate, check, solve
                # print('Генерируем данные для mode=custom')
                d['stepSource']['block']['source']['code'] = \
                    self.generate_check_solve_tab or \
                    custom_genchecksolve(
                        tests=self.tests,
                        checker_function=function,
                        additional_parameter=self.additional_parameter,
                        open_tests=self.open_tests
                    )
                # тесты
                d['stepSource']['block']['source']['test_cases'] = []
                d['stepSource']['block']['source']['samples_count'] = 0

                self.text += self.test_examples(self.tests, open_tests_number=self.open_tests)  # при новых вызовах добавляет новый текст, меняя результат

            case '_':
                raise ValueError(f'mode {self.mode} не существует; только stepik и custom')

        # TODO: выяснить в каком виде загружается тестовый архив
        # d['stepSource']['block']['source']['test_archive'] = []
        # d['stepSource']['block']['tests_archive'] = "/api/step-sources/{}/tests",  # id шага

        d['stepSource']['score'] = self.config.get('score', self.DEFAULT_SCORE)
        d['stepSource']['block']['text'] = markdown_to_html(self.text)

        return d


    def test_examples(self, tests, open_tests_number: int = -1):
        """Возвращает тесты в html виде для вставки в условие в секции Тестовые данные.
        Видимые тесты можно указать сколько или все (-1) в опции open_tests_number.
        -2 - раздел Тестовые данные вообще отсутствует.
        """
        if open_tests_number == -2:
            return ''
        elif open_tests_number == 0:
            return self.TEST_EXAMPLE_SECTION_TEMPLATE.format('Данные закрыты.')

        # форматируем данные тестов для первого теста и секции Тестовые данные
        # первый тест виден
        number = 1
        test = tests[0]
        first_test = self.TEST_EXAMPLE_TEMPLATE.format(number=number, test_input=test[0], test_output=test[1])

        open_tests = tests[1:open_tests_number] if open_tests_number > 0 else tests[1:]
        tests_text = '\n'.join([
            self.TEST_EXAMPLE_TEMPLATE.format(number=number, test_input=test[0], test_output=test[1])
            for number, test in enumerate(open_tests, 2)
        ])
        # добавляем надпись, что остальные тесты закрыты
        if open_tests_number != -1 and len(tests) > open_tests_number:
            tests_text += self.TEST_CLOSED

        return first_test + self.TEST_EXAMPLE_SECTION_TEMPLATE.format(tests_text)

    def gen_check_solve(self):
        """Возвращает содержимое вкладки Расширенный редактор (generate, check, solve)."""
        function = get_checker_function_by_name(self.checker)

        return  stepik_genchecksolve(checker_function=function, additional_parameter=self.additional_parameter)

    def templates_data(self):
        """Возвращает содержимое вкладки Языки и Шаблоны, записанное в self.template
        или собранное из self.lang, self.code, self.header, self.footer.
        """
        # руками описанная вкладка Языки и Шаблоны
        if self.template:
            # return ''.join (self.template)
            return self.template

        # иначе, если языки не ограничены, вкладка должна быть пуста
        # (а как же блок ::code, он может быть определен вне языка?)
        if self.lang == 'all':
            return ''

        return '\n'.join ([
            '::' + self.lang,
            '::code\n' + self.code,
            '::header\n' + self.part_before,
            '::footer\n' + self.part_after
        ])


class ParseSchemaStepTaskinline(ParseSchema):
    @classmethod
    def tests(cls) -> pp.ParserElement:
        """Scheme """
        sep_input = pp.AtLineStart(pp.Word('-', min=4)) + pp.LineEnd()
        sep_output = pp.AtLineStart(pp.Word('=', min=4)) + pp.LineEnd()
        test_data = (pp.SkipTo(sep_input)('input') + pp.Suppress(sep_input) +
                     pp.SkipTo(sep_output)('output') + pp.Suppress(sep_output))
        test_data.setParseAction(lambda t: [t.input.rstrip(), t.output.rstrip()])
        section_title = cls.section_name('TEST')
        schema = pp.Suppress(section_title) + pp.OneOrMore(test_data)
        return schema

    @classmethod
    def step_taskinline(cls) -> pp.ParserElement:
        """
        text
        TEST
        input1
        ----
        output1
        ====
        input2
        ----
        output2
        ====
        HEADER
        до кода студента
        FOOTER
        после кода студента
        CODE
        шаблон в онлайн редакторе для студента
        GENCHECKSOLVE
        полное содержимое вкладки расширенного редактора, самое приоритетное
        CONFIG:
        checker: checker_float_seq
        additional_parameters: EPS = 0.01
        mode: stepik
        open_tests: 3
        lang: c_valgrind

        to dict
        {
            'text': ['Условие задачи.\nМного строк'],
            'tests': [['input1', 'output1'], ['input2', 'output2']],
            'header': '#include <stdio.h>\ntypedef unsigned long long int llu;\n',
            'footer': 'int main() {\n    printf("hello"); return 0;\n}\n',
            'code': 'void sum (int a, int b)\n{\n\n}\n',
            'genchecksolve': text,
            'config': [
                'checker': checker_float_seq,
                'additional_parameters': 'EPS = 0.01',
                'mode': 'stepik',
                'open_tests': '3',
                'lang': 'c_valgrind'
            ]
        }
        """
        tests = cls.tests()('tests')
        config = cls.config()('config')
        header_title = cls.section_name('HEADER')
        footer_title = cls.section_name('FOOTER')
        code_title = cls.section_name('CODE')
        template_title = cls.section_name('TEMPLATE')  # для чего она нужна???
        genchecksolve_title = cls.section_name('GENCHECKSOLVE')
        section_bound = header_title | footer_title | code_title | template_title | genchecksolve_title | \
                        tests | config | pp.StringEnd()
        header = pp.Suppress(header_title) + pp.SkipTo(section_bound)('header')
        footer = pp.Suppress(footer_title) + pp.SkipTo(section_bound)('footer')
        code = pp.Suppress(code_title) + pp.SkipTo(section_bound)('code')
        template = pp.Suppress(template_title) + pp.SkipTo(section_bound)('template')
        genchecksolve = pp.Suppress(genchecksolve_title) + pp.SkipTo(section_bound)('genchecksolve')
        section = tests & pp.Opt(config) & \
                  pp.Opt(header) & pp.Opt(footer) & pp.Opt(code) & pp.Opt(template) & pp.Opt(genchecksolve)
        # section = tests & config & header & footer & code

        # условие - все до первой секции
        text_bound = cls.quoted() | section_bound
        text_part = pp.SkipTo(text_bound)
        # это не помогло починить пропажу \n перед началом quoted:
        statement = (text_part + pp.ZeroOrMore(cls.quoted + text_part))("text")
        # без этого пропадает \n перед началом ```
        statement.setParseAction(lambda t: '\n'.join(map(str.strip, t.as_list())))
        schema = statement + pp.OneOrMore(section)
        return schema

    @classmethod
    def parse_step_testinline(cls, text: str) -> ParseResults:
        try:
            return cls.step_taskinline().parseString(text).as_dict()
        except pp.ParseException as e:
            parse_error(1, text, e.msg)


