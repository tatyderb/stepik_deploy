# Шаг QUIZ (выбор ответа)

Шаг типа `QUIZ` (или `choice`) предлагает пользователю выбрать один или несколько правильных ответов из предложенных вариантов. Система автоматически проверяет ответ, сравнивая его с эталонными значениями, указанными в `source`.

> **Общие поля** (`id`, `lesson`, `position`, `status`, `text`, `video`, `viewed_by`, `passed_by`, `discussions_count`, `num_grades`) описаны в разделе ["Текстовые шаги в Stepik"](https://stepik.org/lesson/2281192/step/1?unit=2315580). Здесь рассматриваются только поля, специфичные для шагов-тестов.

#### Пример шага QUIZ из API Stepik

```json
{
  "id": 8220263,
  "lesson": 1950068,
  "position": 3,
  "status": "ready",
  "block": {
    "name": "choice",
    "text": "\u003Ch2\u003EВыбор нескольких ответов\u003C/h2\u003E\n\u003Cp\u003EВыберите все правильные ответы.\u003C/p\u003E\n\u003Cp\u003E? = 12\u003C/p\u003E",
    "video": null,
    "options": {
      "is_multiple_choice": true
    },
    "subtitle_files": [],
    "is_deprecated": false,
    "source": {
      "options": [
        {
          "is_correct": true,
          "text": "\u003Cp\u003E6 * 2\u003C/p\u003E",
          "feedback": ""
        },
        {
          "is_correct": false,
          "text": "\u003Cp\u003E7 - 18\u003C/p\u003E",
          "feedback": ""
        },
        {
          "is_correct": false,
          "text": "\u003Cp\u003E1 + 2\u003C/p\u003E",
          "feedback": ""
        },
        {
          "is_correct": true,
          "text": "\u003Cp\u003E9 + 3\u003C/p\u003E",
          "feedback": ""
        }
      ],
      "is_always_correct": false,
      "is_html_enabled": true,
      "sample_size": 4,
      "is_multiple_choice": true,
      "preserve_order": false,
      "is_options_feedback": false
    },
    "subtitles": {},
    "tests_archive": null,
    "feedback_correct": "",
    "feedback_wrong": ""
  },
  "cost": 2,
  "viewed_by": 29,
  "passed_by": 20,
  "correct_ratio": 0.714285714285714,
  "discussions_count": 1,
  "num_grades": [0, 0, 0, 0, 1]
}
```

#### Специфичные поля шага QUIZ

`block.name` : Всегда равен `"choice"` — определяет тип шага.

`block.options` : Объект с настройками отображения теста.

* `is_multiple_choice` : `true` / `false` — если `true`, можно выбрать несколько ответов, если `false` — только один.

`block.source` : **Самый важный объект, в котором хранятся варианты ответов и правильные ответы.**

* `options` : Массив объектов, где каждый объект — один вариант ответа.
  * `is_correct` : `true` или `false` — правильный это вариант или нет.
  * `text` : Текст варианта ответа.
  * `feedback` : Индивидуальная обратная связь для этого варианта (пустая строка, если не используется).
* `is_always_correct` : `false` — если `true`, любой ответ считается правильным.
* `is_html_enabled` : `true` — будет ли содержимое шага обрабатываться как HTML-формат.
* `sample_size` : `4` — количество вариантов ответа.
* `preserve_order` : `false` — если `false`, варианты перемешиваются. Если `true` — остаются в заданном порядке.
* `is_options_feedback` : `false` — показывать ли индивидуальную обратную связь для каждого варианта.

`feedback_correct` и `feedback_wrong` : Пустые строки. Здесь можно разместить комментарии для пользователя, которые он увидит после правильного или неправильного ответа

`cost` : `2` — **количество баллов за правильное выполнение шага.**

**Статистика**

`correct_ratio` : `0.714285714285714` — Доля правильных ответов среди всех попыток.

`passed_by` : `20` — Количество пользователей, успешно решивших задачу.
