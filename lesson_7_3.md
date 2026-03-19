### Перед следующими шагами: авторизация

**POST** https://stepik.org/oauth2/token/
Content-Type: application/x-www-form-urlencoded \
Authorization: Basic base64(client_id:client_secret)

grant_type=client_credentials


```json
{
    "client_id": "...",
    "client_secret": "..."
}
```

### 1. Получение ФИО студента и его id

#### 1.1  Получить все решения в классе

GET https://stepik.org/api/submissions?class=11635&page=1

Authorization: Bearer <token>
```json

{
    "meta": {
        "page": 1,
        "has_next": true,
        "has_previous": false
    },
    "submissions": [
        {
            "id": 1515824800,
            "attempt": 1436869583,
            "user": 296745003,
            "step": 123456,
            "score": 1.0,
            "status": "correct"
        },
        {
            "id": 1515824801,
            "attempt": 1436869584,
            "user": 296744444,
            "step": 123457,
            "score": 0.5,
            "status": "wrong"
        }
    ]
}

```
#### 1.2 Получить ID студентов с помощью попыток решения


GET /api/attempts/{attempt_id} \
Authorization: Bearer <token>
``` json
{
    "attempts": [
        {
            "id": 1436869584,
            "user": 296744444,
            "step": 123457
        }
    ]
}
```
#### 1.3 По ID студентов получить ФИО

GET /api/users?ids[]={user_id1} \
Authorization: Bearer <token>

```json
{
    "users": [
        {
            "id": 123456789,
            "first_name": "Иван",
            "last_name": "Иванов",
            "full_name": "Иван Иванов"
        }
    ]
}
```

### 2. Получение решений студента по шагу

GET /api/submissions?user={student_id}&step={step_id} \
Authorization: Bearer <token>
```json
{
    "submissions": [
        {
            "id": 1515824800,
            "score": 1.0,
            "status": "correct",          
        },
        {
            "id": 1515824780,
            "score": 0.5,
            "status": "wrong"
        }
    ]
}
```

### 3. Получение баллов студента за шаг
GET /api/submissions?user={user_id}&step={step_id}&order=desc&page={page_id} \
Authorization: Bearer <token>
``` json
{
    "submissions": [
        {
            "id": 1515824800,
            "score": 1.0,
            "status": "correct"
        }
    ]
}
```

