### Шаг SPACE (задача на заполнение пропусков)

В этом типе задач пользователю предлагается выбрать правильный ответ из выпадающего списка или заполнить пропуск, введя ответ вручную. Система автоматически проверяет на правильность ответ, сравнивая его с эталонным.

> **Общие поля** (`id`, `lesson`, `position`, `status`, `text`, `video`, `viewed_by`, `passed_by`, `discussions_count`, `num_grades`) описаны в разделе ["Текстовые шаги в Stepik"](https://stepik.org/lesson/2281192/step/1?unit=2315580). Здесь рассматриваются только поля, специфичные для задач на сортировку.

#### Пример шага SPACE из API Stepik

```json
{
  "id": 9485450,
  "lesson": 2074851,
  "position": 2,
  "status": "ready",
  "block": {
    "name":"fill-blanks",
    "text":"Заполните пропуски",
    "video":null,
    "options":{},
    "subtitle_files":[],
    "is_deprecated":false,
    "source": {
        "components":[
        {
            "type":"text",
            "text":"Поэму \"Кому на Руси жить хорошо\" написал ",
            "options":[]
        },
        {
            "type":"input",
            "text":"",
            "options":[
                {"text":"Пушкин","is_correct":true},
                {"text":"А.С. Пушкин","is_correct":true},
                {"text":"А. С. Пушкин","is_correct":true},
                {"text":"Александр Сергеевич Пушкин","is_correct":true}
            ]
        },
        {
            "type":"select",
            "text":"",
            "options":[
                {"text":"Пушкин","is_correct":false},
                {"text":"Тургеньев","is_correct":false},
                {"text":"Некрасов","is_correct":true}
            ]
        }
        ],
        "is_case_sensitive":false,
        "is_detailed_feedback":false,
        "is_partially_correct":false
    },
  },
  "cost": 2,
  "viewed_by": 15,
  "passed_by": 12,
  "correct_ratio": 0.8,
  "discussions_count": 0,
  "num_grades": [0, 0, 0, 0, 1]
}
```
#### Специфичные поля шага SPACE

* **`block.name`** : `"fill-blanks"` — Тип шага. Для задачи на заполнение пробела всегда `"fill-blanks"`.

* **`block.source`** : Объект, содержащий структуру шага и настройки проверки.

  * **`components`** : Массив компонентов, из которых собирается шаг. Каждый компонент имеет поле `type`:

    * `"text"` — Обычный текст. Содержится в поле `text`.
    * `"input"` — Поле для ввода текста (без выпадающего списка). Все опции в `options` являются правильными (`is_correct` всегда `true`).
    * `"select"` — Выпадающий список. Опции содержат `text` и флаг `is_correct`.

  * **`is_case_sensitive`** : `true` / `false` — Учитывать ли регистр при сравнении ответов.

  * **`is_detailed_feedback`** : `true` / `false` — Показывать ли для каждого пропуска, верно он заполнен или нет.

  * **`is_partially_correct`** : `true` / `false` — Начислять ли частичный балл за частично верный ответ.

* **`cost`** : Баллы за выполнение шага.