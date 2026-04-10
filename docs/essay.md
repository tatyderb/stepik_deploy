### Шаг ESSAY (свободный ответ)

В этом типе задач пользователю предлагается написать развёрнутый ответ (текст, эссе, решение задачи), который затем проверяется преподавателем вручную или автоматически с помощью специального чекера.

> **Общие поля** (`id`, `lesson`, `position`, `status`, `text`, `video`, `viewed_by`, `passed_by`, `discussions_count`, `num_grades`) описаны в разделе ["Текстовые шаги в Stepik"](https://stepik.org/lesson/2281192/step/1?unit=2315580). Здесь рассматриваются только поля, специфичные для задач со свободным ответом.

#### Пример шага ESSAY из API Stepik

```json
{
  "id": 2005803,
  "lesson": 1978058,
  "position": 4,
  "status": "ready",
  "block": {
    "name": "free-answer",
    "text": "<h2>Напишите эссе</h2>\n<p>Опишите свои впечатления от курса.</p>",
    "video": null,
    "options": null,
    "source": {
      "is_attachments_enabled": false,
      "is_html_enabled": true,
      "manual_scoring": false
    }
  },
  "cost": 5,
  "viewed_by": 42,
  "passed_by": 38,
  "correct_ratio": 0.9047619047619048,
  "discussions_count": 3,
  "num_grades": [0, 0, 1, 2, 1]
}
```


#### Специфичные поля шага ESSAY
* **`block.name`** : `"free-answer"` — Тип шага. Для задачи со свободным ответом всегда `"free-answer"`.

* **`block.source`** : Объект, содержащий настройки проверки ответа.

  * `is_attachments_enabled` : `false` — Разрешена ли загрузка вложений (файлов) к ответу.

  * `is_html_enabled` : `true` — Разрешено ли использование HTML-разметки в ответе студента.

  * `manual_scoring` : `false` — Требуется ли ручная проверка ответа преподавателем.

* **`cost`**  : `5` — Баллы за выполнение шага.
