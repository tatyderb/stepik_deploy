### Шаг Taskinline (задача на программирование)

Шаг типа `Taskinline` предлагает пользователю написать программный код, который затем автоматически проверяется системой. Это основной тип задач на программирование в Stepik.

> **Общие поля** (`id`, `lesson`, `position`, `status`, `text`, `video`, `viewed_by`, `passed_by`, `discussions_count`, `num_grades`) описаны в разделе ["Текстовые шаги в Stepik"](https://stepik.org/lesson/2281192/step/1?unit=2315580). Здесь рассматриваются только поля, специфичные для задач на программирование.

#### Пример шага Taskinline из API Stepik

```json
{
  "id": 1234567,
  "lesson": 1950070,
  "position": 4,
  "status": "ready",
  "block": {
    "name": "code",
    "text": "<h2>Напишите функцию</h2>\n<p>Напишите функцию, которая вычисляет модуль числа.</p>\n<p>Функцию нужно написать на языке C.</p>\n<pre><code class=\"language-cpp\">int module(int x); \n</code></pre>",
    "video": null,
    "options": null,
    "source": {
      "code": "\n\ndef check_asis(reply, clue):\n    \"\"\"Сравнение текста, без пробельных символов в конце текста.\"\"\"\n    return reply.strip() == clue.strip()\n        \n        \n# This is a sample Code Challenge\n# Learn more: https://stepik.org/lesson/9172\n# Ask your questions via help@stepik.org\n\ndef generate():\n    return []\n\ndef check(reply, clue):\n    return check_asis(reply, clue)\n\n# def solve(dataset):\n#     a, b = dataset.split()\n#     return str(int(a) + int(b))        \n    ",
      "execution_time_limit": 5,
      "execution_memory_limit": 256,
      "samples_count": 2,
      "templates_data": "::c\n::code\nint module(int x) {\n    // здесь нужно написать код\n}\n::header\n#include <stdio.h>\nint module(int x);\n::footer\nint main()\n{\n    int x;\n    scanf(\"%d\", &x);\n    printf(\"%d\\n\", module(x));\n    return 0;\n}",
      "is_time_limit_scaled": true,
      "is_memory_limit_scaled": true,
      "is_run_user_code_allowed": true,
      "manual_time_limits": [],
      "manual_memory_limits": [],
      "test_archive": [],
      "test_cases": [
        ["-5", "5"],
        ["21", "21"]
      ]
    },
    "feedback_correct": "",
    "feedback_wrong": ""
  },
  "cost": 10,
  "viewed_by": 120,
  "passed_by": 85,
  "correct_ratio": 0.708,
  "discussions_count": 5,
  "num_grades": [0, 0, 2, 8, 15]
}
```

#### Специфичные поля шага Taskinline

**`block.name`** : Всегда равен `"code"` — определяет тип шага как задачу на программирование.

**`block.source`** : **Самый важный объект, в котором хранятся данные для проверки кода.**

* `code` : Строка с Python-кодом проверяющей функции. Обычно содержит функции `check(reply, clue)` и `generate()`. `check` возвращает `True`, если ответ правильный. `generate` возвращает список тестов (если тесты не заданы в `test_cases`).
* `execution_time_limit` : `5` — Ограничение времени выполнения кода студента (в секундах).
* `execution_memory_limit` : `256` — Ограничение памяти (в мегабайтах).
* `samples_count` : `2` — Количество открытых тестов, которые видит пользователь. Обычно соответствует первым тестам из `test_cases`.
* `templates_data` : Строка с шаблонами кода для разных языков программирования. Формат описан ниже.
* `is_time_limit_scaled` : `true` — Масштабировать ли лимит времени в зависимости от сложности тестов.
* `is_memory_limit_scaled` : `true` — Масштабировать ли лимит памяти.
* `is_run_user_code_allowed` : `true` — Разрешён ли запуск пользовательского кода на сервере.
* `manual_time_limits` : `[]` — Массив ручных ограничений времени для отдельных тестов (пустой, если не используются).
* `manual_memory_limits` : `[]` — Массив ручных ограничений памяти для отдельных тестов.
* `test_archive` : `[]` — Архив с тестами (обычно пуст, тесты хранятся в `test_cases`).
* `test_cases` : Массив тестов. Каждый тест — массив из двух строк: `["входные данные", "ожидаемый вывод"]`.

**Ограничения попыток**

`is_solutions_unlocked` : `true` — Открыты ли решения после прохождения.

`solutions_unlocked_attempts` : `4` — Через сколько попыток открываются решения.

`max_submissions_count` : `3` — Максимальное количество попыток.

`has_submissions_restrictions` : `false` — Есть ли ограничения на количество попыток.

### Формат `templates_data`

Поле `templates_data` содержит шаблоны кода для разных языков программирования. Синтаксис:

```
::<язык>
::header
<код, который будет перед кодом прльзователя>
::footer
<код, который будет после кода пользователя>
::code
<шаблон, который видит пользователь>
```

**Пример для одного языка:**

```
::c
::code
int module(int x) {
    // здесь нужно написать код
}
::header
#include <stdio.h>
int module(int x);
::footer
int main()
{
    int x;
    scanf("%d", &x);
    printf("%d\n", module(x));
    return 0;
}
```

**Пример для нескольких языков:**

```
::c
::header
#include <stdio.h>
int module(int x);
::footer
int main() {
    int x;
    scanf("%d", &x);
    printf("%d\n", module(x));
    return 0;
}
::code
int module(int x) {
    // здесь нужно написать код
}

::c++
::header
#include <iostream>
int module(int x);
::footer
int main() {
    int x;
    std::cin >> x;
    std::cout << module(x) << std::endl;
    return 0;
}
::code
int module(int x) {
    // здесь нужно написать код
}
```
