import os
import requests
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_ID = os.getenv("INSTAGRAM_ID")
IMAGE_URL = "https://i.ibb.co/DDn29BJb/imagens-prontas-teste.jpg"

print("✅ Token carregado:", "SIM" if ACCESS_TOKEN else "NÃO")
print("✅ Instagram ID:", INSTAGRAM_ID)

if not ACCESS_TOKEN or not INSTAGRAM_ID:
    print("❌ ERRO: ACCESS_TOKEN ou INSTAGRAM_ID não carregados.")
    exit()

print("📌 Enviando requisição de mídia...")

url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ID}/media"
payload = {
    "image_url": IMAGE_URL,
    "caption": "Post de teste enviado pela API ✅",
    "access_token": ACCESS_TOKEN
}

response = requests.post(url, data=payload)
print("Resposta:", response.text)

if "id" in response.text:
    print("✅ Mídia criada com sucesso!")
else:
    print("❌ Erro ao criar mídia.")
