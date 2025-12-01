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
- match_substring - Сверка по фрагменту
- use_re - Проверка по регулярному выражению
- case_sensitive - Учитывать регистр и различать заглавные и строчные буквы
- is_text_disabled - Запретить ввод ответа в текстовое поле
- is_file_disabled - Запретить посылку файла с ответом

Stepik использует следующие комбинации is_text_disabled и is_file_disabled:
- По умолчанию (для бесплатных курсов) только текст: is_text_disabled = false, is_file_disabled = true
- Только файл: is_text_disabled = true, is_file_disabled = false
- Текст или файл: is_text_disabled = false, is_file_disabled = false

## STRING Простой случай
Как называется шахматная фигура, которая ходит по вертикали и горизонтали?
ANSWER: ладья


## STRING Демонстрация опции CONFIG
Назовите столицу России
ANSWER: Москва
CONFIG
case_sensitive: true

## STRING Многострочные ответы
Напишите три строки стиховорения, которые следуют после этих строк:

Мороз и солнце; день чудесный!
Еще ты дремлешь, друг прелестный —
Пора, красавица, проснись:
[ваши 3 строки]
ANSWER: 
Открой сомкнуты негой взоры
Навстречу северной Авроры,
Звездою севера явись!
CONFIG
score: 5

## STRING Регулярные выражения
Можно создать сверку по регулярному выражению, например:
Напишите север или юг
ANSWER: север|юг
CONFIG
use_re: true



## STRING Множественные ответы
Как называется величина det(A)?
ANSWER: детерминант
ANSWER: определитель

## STRING

Шаг без заголовка.

Первый месяц года?

ANSWER: январь
CONFIG
case_sensitive: false
