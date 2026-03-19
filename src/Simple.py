import requests
import yaml
import os

# 1. Берем ключи из того файла, который создал скрипт
# Он лежит в stepik_deploy/src/auth.yaml
auth_path = os.path.join("stepik_deploy", "src", "auth.yaml")
with open(auth_path, "r") as f:
    config = yaml.safe_load(f)

client_id = config["client_id"]
client_secret = config["client_secret"]

# 2. Получаем токен напрямую
auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
resp = requests.post(
    "https://stepik.org/oauth2/token/",
    data={"grant_type": "client_credentials"},
    auth=auth,
)
token = resp.json().get("access_token")

# 3. Читаем твой файл
with open("part2.md", "r", encoding="utf-8") as f:
    content = f.read()

# 4. Отправляем на твой урок 2238404
headers = {"Authorization": f"Bearer {token}"}
data = {"step-source": {"block": {"name": "text", "text": content}, "lesson": 2238404}}

r = requests.post("https://stepik.org/api/step-sources", json=data, headers=headers)

if r.status_code == 201:
    print("✅ ВСЁ! Улетело на Stepik. Проверяй сайт!")
else:
    print(f"❌ Ошибка {r.status_code}: {r.text}")
