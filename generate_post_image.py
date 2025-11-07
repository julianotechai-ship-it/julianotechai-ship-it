import os
import time
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

# ===============================
# CONFIGURAÇÕES
# ===============================

CLOUDINARY_UPLOAD_URL = "https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUD_PRESET = os.getenv("UPLOAD_PRESET")

INSTAGRAM_ID = os.getenv("INSTAGRAM_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

GENERATED_FOLDER = "generated_images"
USED_IMAGES_FILE = "used_images.txt"

# ===============================
# FUNÇÕES
# ===============================

def gerar_imagem_automatica():
    print("🚀 Gerando imagem automática...")
    result = subprocess.run(["python", "generate_post_image.py"], capture_output=True, text=True)
    print(result.stdout)

def pegar_ultima_imagem():
    print("📂 Buscando última imagem gerada...")
    imagens = [f for f in os.listdir(GENERATED_FOLDER) if f.lower().endswith((".jpg", ".png"))]
    if not imagens:
        raise Exception("Nenhuma imagem encontrada na pasta generated_images")

    imagens.sort(reverse=True)
    caminho = os.path.join(GENERATED_FOLDER, imagens[0])
    print(f"✅ Imagem selecionada: {caminho}")
    return caminho

def imagem_ja_usada(caminho):
    if not os.path.exists(USED_IMAGES_FILE):
        return False
    with open(USED_IMAGES_FILE, "r") as f:
        usadas = f.read().splitlines()
    return os.path.basename(caminho) in usadas

def marcar_como_usada(caminho):
    with open(USED_IMAGES_FILE, "a") as f:
        f.write(os.path.basename(caminho) + "\n")

def upload_cloudinary(caminho):
    print("🌩 Enviando imagem para Cloudinary...")

    url_upload = CLOUDINARY_UPLOAD_URL.format(cloud_name=CLOUD_NAME)

    with open(caminho, "rb") as file:
        response = requests.post(
            url_upload,
            files={"file": file},
            data={"upload_preset": CLOUD_PRESET}
        )

    if response.status_code != 200:
        raise Exception(f"Erro ao enviar para Cloudinary: {response.text}")

    img_url = response.json()["secure_url"]
    print(f"✅ Upload feito: {img_url}")
    return img_url

def criar_midia(img_url):
    print("🧩 Criando mídia no Instagram...")

    create_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_ID}/media"
    params = {
        "image_url": img_url,
        "caption": "Recomeço é coragem em movimento. #recomeço #reflexão",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(create_url, data=params)

    if response.status_code != 200:
        raise Exception(f"Erro ao criar mídia: {response.text}")

    creation_id = response.json()["id"]
    print(f"✅ Mídia criada: {creation_id}")
    return creation_id

def publicar_midia(creation_id):
    print("📤 Publicando no Instagram...")

    publish_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_ID}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(publish_url, data=params)

    if response.status_code != 200:
        raise Exception(f"Erro ao publicar mídia: {response.text}")

    print("✅ Post publicado com sucesso!")

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================

def executar():
    gerar_imagem_automatica()

    caminho = pegar_ultima_imagem()

    if imagem_ja_usada(caminho):
        print("⚠ Essa imagem já foi usada. Gerando outra...")
        return

    img_url = upload_cloudinary(caminho)

    creation_id = criar_midia(img_url)

    print("⏳ Aguardando processamento da mídia...")
    time.sleep(10)

    publicar_midia(creation_id)

    marcar_como_usada(caminho)
    print("\n✅✅✅ PROCESSO FINALIZADO COM SUCESSO ✅✅✅")

# ===============================
# INICIAR
# ===============================

if __name__ == "__main__":
    executar()
