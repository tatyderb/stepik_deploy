# Как учиться без степика

## Скачайте

### Содержимое курса

Возьмите содержимое курса из репозитория

[https://github.com/tatyderb/conline_new](https://github.com/tatyderb/conline_new)

### Скачайте файл `run_all_tests.sh`

[run_all_tests.sh](https://github.com/tatyderb/stepik_deploy/blob/main/utils/run_all_tests.sh)

Запускать его будете в терминале Linux/UNIX/Mac (у кого Windows - под WSL или cygwin).

Один раз, после того, как скачали файл `run_all_tests.sh` дайте ему права на исполнение командой в терминале:
```
chmod +x run_all_tests.sh
```

## Из md файла урока степика получаем файлы с тестами

### Файл урока - делаем из него файл тестов

Директория `8_arr` - это урок про массивы. Теорию можно читать в файлах. Файлы в формате markdown. Там же в файлах описаны задачи с тестами.

Начало файла начинается с указания, какой именно урок степика он описывает. Нам нужно число 607325 из текста начала файла `8_4_task_lignt.md`

```
# Легкие задачи на массивы

lesson = 607325
lang = c_valgrind
```

Значит файл соответствует  уроку [https://stepik.org/lesson/607325/step/1](https://stepik.org/lesson/607325/step/1), последняя часть URL - номер шага в уроке, нумерация начинается с 1. Когда степик будет устойчиво и быстро работать, вы загрузите туда решения задач.

Шаг типа "задача на программирование" начинается с `## TASKINLINE`. Дальше идет условие задачи. В части `TEST` - что подается на вход и что ожидается на выход. 

Из текста шага нужно извлечь все тесты и, допустим, сохранить их в файл `test.txt`. В первой задаче этого урока содержимое файла `test.txt` будет:

```
5
2 17 18 -4 9
----
2 18 -4
17 9
====
1
10
----
10
====
14
59 48 67 16 33 55 11 45 41 4 20 69 21 61
----
48 16 4 20
59 67 33 55 11 45 41 69 21 61
====
```

`====` - конец одного теста, `----` - разделитель между вводом и ожидаемым выводом.

### Прогоняем все тесты 

Предположим, мы работаем в директории `informatica` с таким содержимым:

```
informatica
|- run_all_tests.sh
|- 8_arr
|   |- 607325-1
|       |- tests.txt
|       |- solution.c
|- a.exe
```

* `tests.txt` вы сделали из файла урока, как описано выше.
* `solution.c` - решение этой задачи
* `a.exe` - результат успешной компиляции (в директории `informatica` выполнили `gcc -g -Wall -Wextra -o a.exe 8_arr/607325-1/solution.c`)

Запуск проверки

```
./run_all_tests.sh ./a.exe 8_arr/607325-1/tests.txt
```
При запуске формируются файлы с входом и ожидаемым выводом для каждого теста. Так что если упало, запускайте прогон одного теста с опцией `-s номер_теста`

**Внимание! Если у вас a.exe в текущей директории, то или добавьте . в PATH, или при запуске скрипта указывайте ./a.exe**

Иначе будет ошибка `--- valgrind (rc=127, errors=unknown, leaked_bytes=0) ---`


## Примеры вывода

### Все тесты успешно отработали

```
taty@tardigrade:/mnt/c/work/courses_my/informatica$ gcc -Wall -Wextra -g 8_arr/8_4_1/solution.c -o a.exe
taty@tardigrade:/mnt/c/work/courses_my/informatica$ ./run_all_tests.sh ./a.exe 8_arr/8_4_1/tests.txt
Test 1: OK
Test 2: OK
Test 3: OK

Passed: 3, Failed: 0, Total: 3
```

### Есть упавшие тесты

```
taty@tardigrade:/mnt/c/work/courses_my/informatica$ ./run_all_tests.sh ./a.exe 8_arr/8_4_1/tests.txt
Test 1: OK
Test 2: OK
Test 3: FAIL
  --- input (/mnt/c/work/courses_my/informatica/8_arr/8_4_1/tests.txt.t3.in) ---
  14
  59 48 67 16 33 55 11 45 41 4 20 69 -21 61
  --- expected (/mnt/c/work/courses_my/informatica/8_arr/8_4_1/tests.txt.t3.out) ---
  48 16 4 20
  59 67 33 55 11 45 41 69 -21 61
  --- actual ---
  48 16 4 20
  59 67 33 55 11 45 41 69 61

Passed: 2, Failed: 1, Total: 3
```

### Запуск одного теста, номер 3

Добавляем `-s 3` в аргументах скрипта.

```
taty@tardigrade:/mnt/c/work/courses_my/informatica$ ./run_all_tests.sh ./a.exe 8_arr/8_4_1/tests.txt -s 3
Test 3: FAIL
  --- input (/mnt/c/work/courses_my/informatica/8_arr/8_4_1/tests.txt.t3.in) ---
  14
  59 48 67 16 33 55 11 45 41 4 20 69 -21 61
  --- expected (/mnt/c/work/courses_my/informatica/8_arr/8_4_1/tests.txt.t3.out) ---
  48 16 4 20
  59 67 33 55 11 45 41 69 -21 61
  --- actual ---
  48 16 4 20
  59 67 33 55 11 45 41 69 61

Passed: 0, Failed: 1, Total: 1
```

### Ошибка valgrind, в ней ничего не понятно

Ошибка в этом скрипте показывается в коротком варианте, например,
```
  --- valgrind (rc=134, errors=unknown, leaked_bytes=0) ---
  *** stack smashing detected ***: terminated
```

Чтобы получить развернутую диагностику, запускайте для отладки отдельно valgrind с данным тестом.

```
valgrind ./a.exe < 8_arr/8_4_1/tests.txt.t1.in
==997== Memcheck, a memory error detector
==997== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==997== Using Valgrind-3.15.0 and LibVEX; rerun with -h for copyright info
==997== Command: ./a.exe
==997==
2 18 -4
2 18 -4
*** stack smashing detected ***: terminated
==997==
==997== Process terminating with default action of signal 6 (SIGABRT)
==997==    at 0x489818B: raise (raise.c:51)
==997==    by 0x4877858: abort (abort.c:79)
==997==    by 0x48E23ED: __libc_message (libc_fatal.c:155)
==997==    by 0x4984B49: __fortify_fail (fortify_fail.c:26)
==997==    by 0x4984B15: __stack_chk_fail (stack_chk_fail.c:24)
==997==    by 0x1092C4: main (solution.c:28)
==997==
==997== HEAP SUMMARY:
==997==     in use at exit: 0 bytes in 0 blocks
==997==   total heap usage: 2 allocs, 2 frees, 5,120 bytes allocated
==997==
==997== All heap blocks were freed -- no leaks are possible
==997==
==997== For lists of detected and suppressed errors, rerun with: -s
==997== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
Aborted (core dumped)
```
