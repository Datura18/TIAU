import json
import os
import requests

with open("users.json", "r") as f:
    users = json.load(f)

TOKEN = os.getenv("BOT_TOKEN")
MESSAGE = "یادت نره غذاتو رزرو کنی!"

for chat_id, active in users.items():
    if active:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": MESSAGE})