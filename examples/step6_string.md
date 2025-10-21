# Шаг STRING - численная задача

lesson = 1977210

## Шаблон

[Текстовая задача](https://stepik.org/lesson/385342/step/1)

```
## STRING Заголовок

Текст условия

ANSWER: строка, несколько строк или регулярное выражение 
CONFIG
use_re: false 
match_substring: false
case_sensitive: false
is_text_disabled: false
is_file_disabled: true
```
- use_re Записано ли регулярное выражение
- match_substring 
- case_sensitive Чувствительность к регистру 
- is_text_disabled
- is_file_disabled


## STRING Простой случай
Как называется шахматная фигура, которая ходит по вертикали и горизонтали?
ANSWER: ладья


## STRING Демонстрация опции CONFIG
Назовите столицу России
ANSWER: Москва
CONFIG
case_sensitive: true

## STRING Многострочные ответы
Вставьте следующие три строки стихотворения:

Мороз и солнце; день чудесный!

Еще ты дремлешь, друг прелестный —

Пора, красавица, проснись:
ANSWER: 
Открой сомкнуты негой взоры
Навстречу северной Авроры,
Звездою севера явись!
CONFIG
score: 5