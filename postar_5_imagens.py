import os
import time
import requests
import shutil
from dotenv import load_dotenv
from pathlib import Path

# carregar .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")
CLOUDINARY_UPLOAD_URL = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"

INPUT_DIR = "input_images"
POSTED_DIR = "posted_images"
os.makedirs(POSTED_DIR, exist_ok=True)

legendas = [
    "A mente cria realidades antes do mundo enxergar...",
    "Disciplina transforma futuro invisível em resultado visível.",
    "Constância vence qualquer talento que para no meio do caminho.",
    "Recomeçar é sinal de força, nunca de fracasso.",
    "O que a mente aceita, o corpo realiza."
]

def upload_cloudinary(caminho):
    with open(caminho, "rb") as img:
        response = requests.post(
            CLOUDINARY_UPLOAD_URL,
            files={"file": img},
            data={"upload_preset": UPLOAD_PRESET}
        )
    r = response.json()
    print("🌩 CLOUDINARY:", r)
    return r.get("secure_url")

def postar_no_instagram(image_url, legenda):
    # criar mídia
    criar_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": legenda,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(criar_url, data=payload)
    res = r.json()
    print("➡ CRIAR:", res)

    if "id" not in res:
        return False

    media_id = res["id"]
    time.sleep(8)

    # publicar
    publicar_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
    r2 = requests.post(publicar_url, data={"creation_id": media_id, "access_token": ACCESS_TOKEN})
    print("➡ PUBLICAR:", r2.json())
    return True

def executar():
    imagens = sorted(os.listdir(INPUT_DIR))[:5]

    if not imagens:
        print("❌ Não há imagens em input_images")
        return

    for idx, img in enumerate(imagens):
        caminho = os.path.join(INPUT_DIR, img)
        legenda = legendas[idx] if idx < len(legendas) else "Recomeço é evolução."

        print(f"\n📤 Subindo {img} para Cloudinary...")
        url = upload_cloudinary(caminho)

        if not url:
            print("❌ Falha no upload")
            continue

        print(f"📤 Postando {img} no Instagram...")
        ok = postar_no_instagram(url, legenda)

        if ok:
            destino = os.path.join(POSTED_DIR, img)
            shutil.move(caminho, destino)
            print(f"✅ {img} movida para posted_images")
        else:
            print(f"❌ Erro ao postar {img}")

        time.sleep(5)

if __name__ == "__main__":
    executar()
