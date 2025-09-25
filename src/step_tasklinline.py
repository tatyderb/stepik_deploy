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
                "code": "# This is a sample Code Challenge\n# Learn more: https://stepik.org/lesson/9173\n# Ask your questions via support@stepik.org\n\nimport math\n\ndef generate():\n    return [] \n\ndef check(reply, clue):\n    if reply == '':\n        return False\n    reply = float(reply)\n    clue = float(clue)\n    return abs(float(reply) - float(clue)) < 0.01\n    #return replay.strip() == clue.strip()\n\ndef dist(x1, y1, x2, y2):\n    dx = x1 - x2\n    dy = y1 - y2\n    return math.sqrt(dx*dx + dy*dy)\n    \n#def solve(dataset):\n#    x1, y1, x2, y2, x3, y3 = map(float, dataset.split())\n#    a = dist(x1, y1, x2, y2)\n#    b = dist(x1, y1, x3, y3)\n#    c = dist(x2, y2, x3, y3)\n#    p = (a + b + c) / 2\n#    return str(math.sqrt(p*(p-a)*(p-b)*(p-c)))",
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

from src.markdown_parsing import ParseSchema, parse_error
from src.step import Step
from src.utils import markdown_to_html

# https://stepik.org/lesson/59057/step/9
LANG_LIMITS = {
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
    DATA_TEMPLATE = {
    "stepSource": {
        "reason_of_failure": "",
        "error": {
            "text": "",
            "code": "",
            "params": {}
        },
        "warnings": [],
        "instruction_id": None,
        "has_instruction": False,
        "cost": DEFAULT_SCORE,
        "is_solutions_unlocked": False,
        "solutions_unlocked_attempts": 3,
        "max_submissions_count": 3,
        "has_submissions_restrictions": False,
        "actions": {
            "edit_instructions": "#",
            "submit": "#"
        },
        "block": {
            "name": "code",
            "text": "",  # условие задачи
            "video": None,
            "options": {    # stepSource.block.options -ограничения на время и память, почему дублируется???
                "execution_time_limit": 5,
                "execution_memory_limit": 256,
                "limits": {
                    "python3": {
                        "time": 15,
                        "memory": 256
                    }
                },
                "code_templates": {
                    "python3": ""  # stepSource.block.options.code_templates тут вставка шаблона для ученика, куда он будет всписывать код, секция CODE
                },
                "code_templates_header_lines_count": {
                    "python3": 0   # от метки ::header до конца, не считая метки сколько линий
                },
                "code_templates_footer_lines_count": {
                    "python3": 0
                },
                "code_templates_options": {},
                "samples": [     # сюда первый тест записать
                    [
                        "3 0 0 4 0 0",
                        "6.0"
                    ]
                ],
                "is_run_user_code_allowed": True
            },
            "subtitle_files": [],
            "source": {
                "code": "", # содержимое последней вкладки: check, solve, generate
                "execution_memory_limit": 256,   # еще одни лимиты....
                "execution_time_limit": 5,
                "is_memory_limit_scaled": True,
                "is_run_user_code_allowed": True,
                "is_time_limit_scaled": True,
                "manual_memory_limits": [],
                "manual_time_limits": [],
                "samples_count": 1,       # сколько надо выводить примеров, оставляем 1
                "templates_data": "",  # содержимое второй вкладки Языки и шаблоны, всей (видимо)
                "test_archive": [],
                "test_cases": [],    # список тестов, [["input1", "output1"], ["input2", "output2"]]
                "are_all_tests_scored": False
            },
            "subtitles": {},
            "tests_archive": "/api/step-sources/1576649/tests",    # id шага
            "feedback_correct": "",
            "feedback_wrong": ""
        },
        "instruction_type": None,
        "lesson_id": "408292",    # id урока
        "position": 6,            # позиция шага от 1
        "status": "ready",
        "instruction": None,
        "lesson": "408292"       # id урока
    }
}

    def __init__(self, header: str = '', skip: bool = False):
        super().__init__(header=header, skip=skip)

    def parse(self, text: str):
        """Обрабатываем содержимое шага, разбирая его на составные части согласно типу."""
        res = ParseSchemaStepTaskinline.parse_step_testinline(text)
        # res={'text': 'Даны два целых числа на одной строке через пробел. Напечатайте их сумму.',
        # 'tests': ['2 3', '5', '-17 -23', '-40'],
        # 'header': '#include <stdio.h>\nint module(int x);',
        # 'footer': 'int main()\n{\n    int x;\n    scanf("%d", &x);\n    printf("%d\n", module(x));\n    return 0;\n}',
        # 'code': 'int module(int x) {\n    // здесь нужно написать код\n}',
        # 'config': [{'lang': 'c'}]}
        print(f'StepTaskinline.parse: {res=}')

        input_data = res['tests'][::1]
        output_data = res['tests'][1::1]
        self.tests = list(zip(input_data, output_data))

        self.config = res.get('config', {})

        self.text = res['text']
        markdown_text = '## ' + self.header + '\n' + self.text + \
                        self.test_examples(self.tests, visible_tests_number=self.config.get('visible_tests_number', -1))

        self.text = markdown_text

    def to_dict(self) -> dict:
        d = self.DATA_TEMPLATE.copy()
        d['stepSource']['block']['text'] = markdown_to_html(self.text)
        # один ответ
        d['stepSource']['block']['source']['options'] = self.options
        d['stepSource']['block']['source']['sample_size'] = len(self.options)
        d['stepSource']['block']['source']['is_multiple_choice'] = self.is_multiple_choice

        d['stepSource']['score'] = self.DEFAULT_SCORE

        return d

    def test_examples(self, tests, visible_tests_number: int = -1):
        """Возвращает тесты в html виде для вставки в условие в секции Тестовые данные.
        Видимые тесты можно указать сколько или все (-1) в опции visible_tests_number.
        -2 - раздел Тестовые данные вообще отсутствует.
        """
        if visible_tests_number == -2:
            return ''
        elif visible_tests_number == 0:
            return self.TEST_EXAMPLE_SECTION_TEMPLATE.format('Данные закрыты.')

        # форматируем данные тестов для секции Тестовые данные
        visible_tests = tests[:visible_tests_number] if visible_tests_number > 0 else tests
        tests_text = '\n'.join([
            self.TEST_EXAMPLE_TEMPLATE.format(number=number, test_input=test[0], test_output=test[1])
            for number, test in enumerate(visible_tests, 1)
        ])
        # добавляем надпись, что остальные тесты закрыты
        if visible_tests_number != -1 and len(tests) > visible_tests_number:
            tests_text += self.TEST_CLOSED

        return self.TEST_EXAMPLE_SECTION_TEMPLATE.format(tests_text)


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
        tests = cls.tests()('tests')
        config = cls.config()('config')
        header_title = cls.section_name('HEADER')
        footer_title = cls.section_name('FOOTER')
        code_title = cls.section_name('CODE')
        section_bound = header_title | footer_title | code_title | tests | config | pp.StringEnd()
        header = pp.Suppress(header_title) + pp.SkipTo(section_bound)('header')
        footer = pp.Suppress(footer_title) + pp.SkipTo(section_bound)('footer')
        code = pp.Suppress(code_title) + pp.SkipTo(section_bound)('code')
        section = tests & pp.Opt(config) & pp.Opt(header) & pp.Opt(footer) & pp.Opt(code)
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

