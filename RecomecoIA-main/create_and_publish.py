import os
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

PAGE_ID = os.getenv("PAGE_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CLOUDINARY_UPLOAD_URL = os.getenv("CLOUDINARY_UPLOAD_URL")
CLOUDINARY_UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")

BASE_IMAGES_DIR = "base_images"
GENERATED_DIR = "generated_images"
FONTS_DIR = "fonts"
FONT_PATH = os.path.join(FONTS_DIR, "PlayfairDisplay-Italic.ttf")

# Escolhe uma frase do arquivo frases.txt
def pick_random_phrase():
    with open("frases.txt", "r", encoding="utf-8") as f:
        frases = f.readlines()
    return random.choice(frases).strip()

# Escolhe uma imagem base aleatória
def pick_random_image():
    imagens = os.listdir(BASE_IMAGES_DIR)
    return os.path.join(BASE_IMAGES_DIR, random.choice(imagens))

# Cria a imagem final com frase e assinatura
def create_post_image():
    frase = pick_random_phrase()
    base_image_path = pick_random_image()
    original = Image.open(base_image_path)
    draw = ImageDraw.Draw(original)

    font = ImageFont.truetype(FONT_PATH, 110)

    largura, altura = original.size
    text_w, text_h = draw.textsize(frase, font=font)
    pos = ((largura - text_w) / 2, (altura - text_h) / 2)

    draw.text(pos, frase, font=font, fill="white")

    assinatura = "@iamjulianocezarh"
    font_ass = ImageFont.truetype(FONT_PATH, 80)
    draw.text((50, altura - 150), assinatura, font=font_ass, fill="white")

    if not os.path.exists(GENERATED_DIR):
        os.makedirs(GENERATED_DIR)

    filename = f"post_{int(time.time())}.jpg"
    save_path = os.path.join(GENERATED_DIR, filename)
    original.save(save_path)

    return save_path, frase

# Upload da imagem para Cloudinary
def upload_to_cloudinary(image_path):
    with open(image_path, "rb") as img:
        response = requests.post(
            CLOUDINARY_UPLOAD_URL,
            files={"file": img},
            data={"upload_preset": CLOUDINARY_UPLOAD_PRESET}
        )
    return response.json()["secure_url"]

# Cria a mídia no Instagram
def create_media(image_url, caption):
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload).json()
    return res["id"]

# Publica a mídia gerada
def publish_media(creation_id):
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload).json()
    return res

# Execução completa
if __name__ == "__main__":
    print("🚀 Gerando imagem...")
    img_path, frase = create_post_image()

    print("☁ Enviando imagem para Cloudinary...")
    image_url = upload_to_cloudinary(img_path)

    hashtags = "#recomeço #força #fé #propósito #mentalidade #inspiração"
    caption = f"{frase}\n\n{hashtags}"

    print("🤖 Criando mídia no Instagram...")
    creation_id = create_media(image_url, caption)

    print("📌 Publicando imagem...")
    publish_response = publish_media(creation_id)

    print("✅ Postagem concluída!")
    print("🖼 Imagem:", img_path)
