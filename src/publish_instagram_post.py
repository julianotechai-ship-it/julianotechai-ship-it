import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_ID = os.getenv("INSTAGRAM_ID")

# coloque aqui o ID que apareceu no seu terminal
MEDIA_ID = "17959835484049722"  

publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ID}/media_publish"

params = {
    "creation_id": MEDIA_ID,
    "access_token": ACCESS_TOKEN
}

response = requests.post(publish_url, params=params)

print("📌 Publicando mídia...")
print("Resposta:", response.text)
