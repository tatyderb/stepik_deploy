# SQL: добавление пользователя
lesson: 0

## SQL Добавление пользователя

Добавьте в таблицу `users` пользователя с именем `Fluttershy`.
Существующие записи должны сохраниться.

INIT
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20)
);

INSERT INTO users (name)
VALUES ('Rainbow Dash'), ('Twilight Sparkle');

SOLUTION
INSERT INTO users (name)
VALUES ('Fluttershy');

CHECK
def check(query, result):
    if "insert" not in query.lower():
        return False, "Use INSERT INTO statement to add a new row"
    count = cursor.execute("select * from users where id=3")
    if cursor.fetchone() == (3, "Fluttershy"):
        return True
    if count == 0:
        return False, "Cannot find a record with id=3"
    return False, "Inserted record is incorrect"

CONFIG
score: 1
allow_any_query: true
allow_multiple_queries: false
