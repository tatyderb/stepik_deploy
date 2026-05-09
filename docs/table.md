### Шаг TABLE (табличная задача)

В этом типе задач пользователю предлагается заполнить таблицу, отмечая ячейки, которые соответствуют правильным ответам. Система автоматически проверяет правильность заполнения всех ячеек.

> **Общие поля** (`id`, `lesson`, `position`, `status`, `text`, `video`, `viewed_by`, `passed_by`, `discussions_count`, `num_grades`) описаны в разделе ["Текстовые шаги в Stepik"](https://stepik.org/lesson/2281192/step/1?unit=2315580). Здесь рассматриваются только поля, специфичные для табличных задач.

#### Пример шага TABLE из API Stepik

```json
{
  "id": 9485455,
  "lesson": 2220076,
  "position": 2,
  "status": "ready",
  "block": {
    "name": "table",
    "text": "<h2>Несколько ответов в ряду</h2>",
    "video": null,
    "options": {},
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
  },
  "cost": 1,
  "viewed_by": 42,
  "passed_by": 38,
  "correct_ratio": 0.904,
  "discussions_count": 2,
  "num_grades": [0, 0, 1, 2, 1]
}
```
#### Специфичные поля шага TABLE

* **`block.name`** : `"table"` — Тип шага. Для табличной задачи всегда `"table"`.

* **`block.source`** : Объект, содержащий данные для проверки ответа.

  * `description` : Заголовок первого столбца (строки таблицы).

  * `columns` : Массив объектов, описывающих колонки таблицы.

    * `name` : Название колонки (может содержать HTML-разметку).

  * `rows` : Массив объектов, каждый из которых представляет одну строку таблицы.

    * `name` : Название строки (может содержать HTML-разметку).

    * `columns` : Массив объектов, описывающих ячейки строки.

      * `choice` : `true` / `false` — Является ли ячейка правильным ответом.

  * `options` : Объект с настройками отображения и проверки таблицы.

    * `is_checkbox` : `true` / `false` — Можно ли выбрать несколько ячеек в одной строке.

    * `is_randomize_rows` : `true` / `false` — Перемешивать ли строки при отображении.

    * `is_randomize_columns` : `true` / `false` — Перемешивать ли колонки при отображении.

  * `is_always_correct` : `true` / `false` — Считается ли любой ответ верным (используется для опросов и сбора обратной связи).

* **`cost`** : `1` — Баллы за выполнение шага.