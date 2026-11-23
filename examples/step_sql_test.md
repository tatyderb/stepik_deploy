# SQL с автоматической проверкой
lesson: 0

## SQL Суммы заказов

Выведите имя каждого пользователя и сумму его заказов.
Назовите столбцы `name` и `total`. Порядок строк произвольный.

INIT
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(30));
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10, 2));
INSERT INTO users VALUES (1, 'Анна'), (2, 'Борис');
INSERT INTO orders VALUES (1, 1, 10.10), (2, 1, 20.20), (3, 2, 40.00);

SOLUTION
SELECT u.name, SUM(o.amount) AS total
FROM users u JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

TEST
RESULT
----
{
    "columns": ["name", "total"],
    "rows": [["Анна", 30.30], ["Борис", 40.00]],
    "ordered": false,
    "tolerance": 0.001
}
====

CONFIG
score: 2

## SQL Перевод между счетами

Переведите 25 единиц со счёта 1 на счёт 2 двумя UPDATE-запросами.
Остальные счета должны сохраниться.

INIT
CREATE TABLE accounts (id INT PRIMARY KEY, balance DECIMAL(10, 2));
INSERT INTO accounts VALUES (1, 100), (2, 200), (3, 300);

SOLUTION
UPDATE accounts SET balance = balance - 25 WHERE id = 1;
UPDATE accounts SET balance = balance + 25 WHERE id = 2;

TEST
RESULT 1
----
{"affected_rows": 1}
====
RESULT 2
----
{"affected_rows": 1}
====
SELECT id, balance FROM accounts ORDER BY id;
----
[[1, 75], [2, 225], [3, 300]]
====
SELECT SUM(balance) FROM accounts;
----
[[600]]
====

CONFIG
score: 3
allow_any_query: true
allow_multiple_queries: true
