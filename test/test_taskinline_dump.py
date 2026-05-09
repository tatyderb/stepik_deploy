"""
Тесты для экспорта TASKINLINE шагов.
"""

import pytest
from src.export.dump import TaskinlineDump


pytestmark = pytest.mark.step_begin("---1234")


class TestTaskinlineDump:
    """Тесты для экспорта TASKINLINE шагов"""

    def test_simple_task(self):
        """Простая задача"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Сумма</h2><p>Условие</p>",
                "source": {
                    "test_cases": [["2 3", "5"]],
                    "templates_data": "",
                    "code": "",
                    "samples_count": 1
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Сумма

Условие

TEST
2 3
----
5
====

CONFIG
score: 10


"""

        assert result.strip() == expected.strip()

    def test_task_with_header_code_footer(self):
        """Задача с HEADER, CODE, FOOTER"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Модуль</h2>",
                "source": {
                    "test_cases": [["-5", "5"]],
                    "templates_data": "::c\n::header\nHEADER_TEXT\n::footer\nFOOTER_TEXT\n::code\nCODE_TEXT",
                    "code": "",
                    "samples_count": 1
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Модуль

TEST
-5
----
5
====

HEADER
HEADER_TEXT

FOOTER
FOOTER_TEXT

CODE
CODE_TEXT

CONFIG
score: 10
lang: c

"""

        assert result.strip() == expected.strip()

    def test_multilang_template(self):
        """Многоязычная задача: выводится TEMPLATE"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Модуль</h2>",
                "source": {
                    "test_cases": [["-5", "5"]],
                    "templates_data": "::c\n::header\nHEADER_C\n::footer\nFOOTER_C\n::code\nCODE_C\n\n::c++\n::header\nHEADER_CPP\n::footer\nFOOTER_CPP\n::code\nCODE_CPP",
                    "code": "",
                    "samples_count": 1
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Модуль

TEST
-5
----
5
====

TEMPLATE
::c
::header
HEADER_C
::footer
FOOTER_C
::code
CODE_C

::c++
::header
HEADER_CPP
::footer
FOOTER_CPP
::code
CODE_CPP

CONFIG
score: 10


"""

        assert result.strip() == expected.strip()

    def test_custom_mode_stepik(self):
        """mode=stepik: тесты извлекаются из test_cases"""
        data = {
            "block": {
                "name": "code",
                "text": "<h2>Stepik mode</h2>",
                "source": {
                    "test_cases": [
                        ["2 3", "5"],
                        ["-7 10", "3"],
                        ["-2 -3", "-5"],
                        ["7 -10", "-3"]
                    ],
                    "templates_data": "",
                    "code": "",
                    "samples_count": 4
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()
        
        expected = """---1234 TASKINLINE

## Stepik mode

TEST
2 3
----
5
====
-7 10
----
3
====
-2 -3
----
-5
====
7 -10
----
-3
====

CONFIG
score: 10


"""

        assert result.strip() == expected.strip()


    expected_383213_1 = """---1234 TASKINLINE

## Модуль

Напишите функцию **func_sum**, которая возвращает сумму аргументов.

```
int func_sum(int x, int y);
```

TEST
-5 2
----
-3
====

CODE
int func_sum(int x, int y)
{
    // тут нужно написать код
}

HEADER
#include <stdio.h>

int func_sum(int x, int y);

int main()
{
    int a, b;
    scanf("%d%d", &a, &b);
    printf("%d\n", func_sum(a, b));
    return 0;
}

CONFIG
score: 10
lang: c_valgrind
"""

    def test_task_python_code(self):
        """Задача с кодом, чувствительном к отступам. Проверяем соответствие пустых линий в темплите.
        Урок 383213, шаг 1.
        """

        html_statement = """<h2>Модуль</h2>

<p>Напишите функцию <strong>func_sum</strong>, которая возвращает сумму аргументов.</p>

<pre>
<code>int func_sum(int x, int y);
</code></pre>
"""
        template_data = """::c_valgrind
::code
int func_sum(int x, int y)
{
    // тут нужно написать код
}
::header
#include <stdio.h>

int func_sum(int x, int y);

int main()
{
    int a, b;
    scanf("%d%d", &a, &b);
    printf("%d\n", func_sum(a, b));
    return 0;
}
"""
        data = {
            "block": {
                "name": "code",
                "text": html_statement,
                "source": {
                    "test_cases": [["-5 2", "-3"]],
                    "templates_data": template_data,
                    "code": "",
                    "samples_count": 1
                }
            },
            "cost": 10
        }
        exporter = TaskinlineDump(data, 1)
        result = exporter.export()

        assert result.strip() == self.expected_383213_1.strip()

# def test_taskinline_real_json():
#     """Все тот же урок и шаг"""
#
#     text_json = """ {
#   "id": 1444301,
#   "lesson": 383213,
#   "position": 1,
#   "status": "ready",
#   "block": {
#     "name": "code",
#     "text": "<h2></h2>\\n<p><a href=\\"https://stepik.org/lesson/383213/step/1\\" rel=\\"noopener noreferrer nofollow\\">Ссылка на себя</a></p>\\n<p>Напишите функцию <strong>func_sum</strong>, которая возвращает сумму аргументов.</p>\\n<pre><code class=\\"cpp\\">int func_sum(int x, int y);\\n</code></pre>",
#     "video": null,
#     "options": {
#       "execution_time_limit": 5,
#       "execution_memory_limit": 256,
#       "limits": {
#         "c_valgrind": {
#           "time": 10,
#           "memory": 256
#         }
#       },
#       "code_templates": {
#         "c_valgrind": "int func_sum(int x, int y)\\n{\\n    // тут нужно написать код\\n}"
#       },
#       "code_templates_header_lines_count": {
#         "c_valgrind": 9
#       },
#       "code_templates_footer_lines_count": {
#         "c_valgrind": 0
#       },
#       "code_templates_options": {},
#       "samples": [
#         [
#           "2 5",
#           "7"
#         ]
#       ],
#       "is_run_user_code_allowed": true
#     },
#     "subtitle_files": [],
#     "is_deprecated": false,
#     "source": {
#       "code": "\\ndef generate():\\n    return []\\n    \\n\\ndef check(reply, clue):\\n    # return reply.strip() == clue.strip()\\n
# res = [x.strip() for x in reply.strip().splitlines()] == [y.strip() for y in clue.strip().splitlines()]\\n    if res:\\n        retu
# rn True\\n    feedback = f\\"\\\nYou answer was: \\\n{reply}\\\nCorrect answer was: \\\n{clue}\\"\\n    return False, feedback  # feedback
#  will be shown to the learner\\n    \\n\\n# def solve(dataset):\\n#     a, b = dataset.split()\\n#     return str(int(a) + int(b))\\n    ",
#       "execution_memory_limit": 256,
#       "execution_time_limit": 5,
#       "is_memory_limit_scaled": true,
#       "is_run_user_code_allowed": true,
#       "is_time_limit_scaled": true,
#       "manual_memory_limits": [],
#       "manual_time_limits": [],
#       "samples_count": 1,
#       "templates_data": "::c_valgrind\\n::code\\nint func_sum(int x, int y)\\n{\\n    // тут нужно написать код\\n}\\n::header\\n#include
#  <stdio.h>\\nint func_sum(int x, int y);\\nint main()\\n{\\n    int a, b;\\n    scanf(\\"%d%d\\", &a, &b);\\n    printf(\\"%d\\\n\\", func_sum(a, b));\\n    return 0;\\n}\\n\\n",
#       "test_archive": [],
#       "test_cases": [
#         [
#           "2 5",
#           "7"
#         ],
#         [
#           "-3 1",
#           "-2"
#         ]
#       ]
#     },
#     "subtitles": {},
#     "tests_archive": "/api/step-sources/1444301/tests",
#     "feedback_correct": "",
#     "feedback_wrong": ""
#   },
#   "actions": {
#     "edit_instructions": "#",
#     "submit": "#",
#     "comment": "#"
#   },
#   "progress": "77-1444301",
#   "subscriptions": [
#     "31-77-1444301",
#     "30-77-1444301"
#   ],
#   "instruction": null,
#   "session": null,
#   "instruction_type": null,
#   "viewed_by": 2,
#   "passed_by": 2,
#   "correct_ratio": 0.6,
#   "worth": 0,
#   "is_solutions_unlocked": false,
#   "solutions_unlocked_attempts": 3,
#   "has_submissions_restrictions": false,
#   "max_submissions_count": 3,
#   "variation": 1,
#   "variations_count": 1,
#   "is_enabled": true,
#   "needs_plan": null,
#   "num_grades": [
#     0,
#     0,
#     0,
#     0,
#     0
#   ],
#   "user_step_grade": null,
#   "user_step_vote": null,
#   "step_issue": 1423392,
#   "create_date": "2020-07-24T21:47:34Z",
#   "update_date": "2022-01-03T16:26:13Z",
#   "discussions_count": 0,
#   "discussion_proxy": "77-1444301-1",
#   "discussion_threads": [
#     "77-1444301-1",
#     "77-1444301-2"
#   ],
#   "reason_of_failure": "",
#   "error": {
#     "text": "",
#     "code": "",
#     "params": {}
#   },
#   "warnings": [],
#   "cost": 10
# }
# """
#     text_json_resp = '''{\n  "id": 1444301,\n  "lesson": 383213,\n  "position": 1,\n  "status": "ready",\n  "block": {\n    "name": "code",\n    "text":
#  "<h2></h2>\\n<p><a href=\\"https://stepik.org/lesson/383213/step/1\\" rel=\\"noopener noreferrer nofollow\\">Ссылка на себя</a></
# p>\\n<p>Напишите функцию <strong>func_sum</strong>, которая возвращает сумму аргументов.</p>\\n<pre><code class=\\"cpp\\">int func
# _sum(int x, int y);\\n</code></pre>",\n    "video": null,\n    "options": {\n      "execution_time_limit": 5,\n      "execution_me
# mory_limit": 256,\n      "limits": {\n        "c_valgrind": {\n          "time": 10,\n          "memory": 256\n        }\n      },
# \n      "code_templates": {\n        "c_valgrind": "int func_sum(int x, int y)\\n{\\n    // тут нужно написать код\\n}"\n      },\
# n      "code_templates_header_lines_count": {\n        "c_valgrind": 9\n      },\n      "code_templates_footer_lines_count": {\n
#       "c_valgrind": 0\n      },\n      "code_templates_options": {},\n      "samples": [\n        [\n          "2 5",\n          "
# 7"\n        ]\n      ],\n      "is_run_user_code_allowed": true\n    },\n    "subtitle_files": [],\n    "is_deprecated": false,\n
#    "source": {\n      "code": "\\ndef generate():\\n    return []\\n    \\n\\ndef check(reply, clue):\\n    # return reply.strip()
#  == clue.strip()\\n    res = [x.strip() for x in reply.strip().splitlines()] == [y.strip() for y in clue.strip().splitlines()]\\n
#    if res:\\n        return True\\n    feedback = f\\"\\\\nYou answer was: \\\\n{reply}\\\\nCorrect answer was: \\\\n{clue}\\"\\n
#    return False, feedback  # feedback will be shown to the learner\\n    \\n\\n# def solve(dataset):\\n#     a, b = dataset.split(
# )\\n#     return str(int(a) + int(b))\\n    ",\n      "execution_memory_limit": 256,\n      "execution_time_limit": 5,\n      "is_
# memory_limit_scaled": true,\n      "is_run_user_code_allowed": true,\n      "is_time_limit_scaled": true,\n      "manual_memory_li
# mits": [],\n      "manual_time_limits": [],\n      "samples_count": 1,\n      "templates_data": "::c_valgrind\\n::code\\nint func_
# sum(int x, int y)\\n{\\n    // тут нужно написать код\\n}\\n::header\\n#include <stdio.h>\\nint func_sum(int x, int y);\\nint main
# ()\\n{\\n    int a, b;\\n    scanf(\\"%d%d\\", &a, &b);\\n    printf(\\"%d\\\\n\\", func_sum(a, b));\\n    return 0;\\n}\\n\\n",\n
#       "test_archive": [],\n      "test_cases": [\n        [\n          "2 5",\n          "7"\n        ],\n        [\n          "-3
#  1",\n          "-2"\n        ]\n      ]\n    },\n    "subtitles": {},\n    "tests_archive": "/api/step-sources/1444301/tests",\n
#    "feedback_correct": "",\n    "feedback_wrong": ""\n  },\n  "actions": {\n    "edit_instructions": "#",\n    "submit": "#",\n
#  "comment": "#"\n  },\n  "progress": "77-1444301",\n  "subscriptions": [\n    "31-77-1444301",\n    "30-77-1444301"\n  ],\n  "inst
# ruction": null,\n  "session": null,\n  "instruction_type": null,\n  "viewed_by": 2,\n  "passed_by": 2,\n  "correct_ratio": 0.6,\n
#  "worth": 0,\n  "is_solutions_unlocked": false,\n  "solutions_unlocked_attempts": 3,\n  "has_submissions_restrictions": false,\n
# "max_submissions_count": 3,\n  "variation": 1,\n  "variations_count": 1,\n  "is_enabled": true,\n  "needs_plan": null,\n  "num_gra
# des": [\n    0,\n    0,\n    0,\n    0,\n    0\n  ],\n  "user_step_grade": null,\n  "user_step_vote": null,\n  "step_issue": 14233
# 92,\n  "create_date": "2020-07-24T21:47:34Z",\n  "update_date": "2022-01-03T16:26:13Z",\n  "discussions_count": 0,\n  "discussion_
# proxy": "77-1444301-1",\n  "discussion_threads": [\n    "77-1444301-1",\n    "77-1444301-2"\n  ],\n  "reason_of_failure": "",\n  "error": {\n    "text": "",\n    "code": "",\n    "params": {}\n  },\n  "warnings": [],\n  "cost": 10\n}'''
#
#     import json
#     # t = text_json.replace('\n', '\\n').replace('\r', '\\r')
#     # print(t)
#     data = json.loads(text_json)
#     exporter = TaskinlineDump(data, 1)
#     result = exporter.export()
