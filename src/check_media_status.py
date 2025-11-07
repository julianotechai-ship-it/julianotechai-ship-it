import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
MEDIA_ID = "17959835484049722"  # coloque aqui seu media id

url = f"https://graph.facebook.com/v19.0/{MEDIA_ID}"
params = {
    "fields": "status_code,status",
    "access_token": ACCESS_TOKEN
}

print("📌 Checando status da mídia...")
response = requests.get(url, params=params)
print("Resposta:", response.text)
