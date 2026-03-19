import requests
import yaml
import os
import json

# --- 1. НАСТРОЙКИ (замените на ваши ID) ---
USER_ID = 296745003  # Ваш ID (из ссылки профиля)
STEP_ID = 9721252  # ID шага (из логов деплоя)

# --- 2. АВТОРИЗАЦИЯ ---
# Проверяем наличие файла с ключами в папке src или в текущей
creds_path = "src/auth.yaml" if os.path.exists("src/auth.yaml") else "auth.yaml"

if not os.path.exists(creds_path):
    print(f"Ошибка: Файл {creds_path} не найден!")
    exit()

with open(creds_path, "r") as f:
    config = yaml.safe_load(f)

# Обработка структуры (с секцией initial или без неё)
if "initial" in config:
    client_id = config["initial"]["client_id"]
    client_secret = config["initial"]["client_secret"]
else:
    client_id = config["client_id"]
    client_secret = config["client_secret"]

# Получаем токен
auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
resp = requests.post(
    "https://stepik.org/oauth2/token/",
    data={"grant_type": "client_credentials"},
    auth=auth,
)
token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# --- 3. ЗАПРОС ПОПЫТОК (ATTEMPTS) ---
print(f"\nЗапрос попыток для пользователя {USER_ID} на шаге {STEP_ID}...")
att_url = f"https://stepik.org/api/attempts?user={USER_ID}&step={STEP_ID}"
att_data = requests.get(att_url, headers=headers).json()

# Выводим «словарь» попыток в консоль
print("\n=== JSON ПОПЫТОК (ATTEMPTS) ===")
print(json.dumps(att_data, indent=4, ensure_ascii=False))

# --- 4. ЗАПРОС РЕШЕНИЙ (SUBMISSIONS) ---
print(f"\nЗапрос последних")
