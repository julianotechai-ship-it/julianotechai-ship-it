import os
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import requests
import time
from dotenv import load_dotenv
import textwrap

load_dotenv()

# ========================
# CONFIGURAÇÕES DO PROJETO
# ========================
BASE_IMAGES = "base_images"
GENERATED_FOLDER = "generated_images"
FONTS_FOLDER = "fonts"

FONT_CINZEL = os.path.join(FONTS_FOLDER, "Cinzel-VariableFont_wght.ttf")
FONT_PLAYFAIR = os.path.join(FONTS_FOLDER, "PlayfairDisplay-Italic.ttf")

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("IG_USER_ID")
CLOUDINARY_UPLOAD_URL = os.getenv("CLOUDINARY_UPLOAD_URL")


# ========================
# LER FRASES DE frases.txt
# ========================
def carregar_frases():
    with open(os.path.join(BASE_IMAGES, "..", "frases.txt"), "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    return linhas


# ==========================================
# ESCOLHER IMAGEM BASE ALEATÓRIA
# ==========================================
def pick_random_image():
    files = [f for f in os.listdir(BASE_IMAGES) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return os.path.join(BASE_IMAGES, random.choice(files))


# ==========================================
# GERAR IMAGEM COM FRASE + ASSINATURA
# ==========================================
def create_post_image():

    frases = carregar_frases()
    frase = random.choice(frases)

    original_path = pick_random_image()
    img = Image.open(original_path)
    draw = ImageDraw.Draw(img)

    # Fonte
    font_frase = ImageFont.truetype(FONT_CINZEL, 70)
    font_assinatura = ImageFont.truetype(FONT_PLAYFAIR, 45)

    # Quebra a frase se ficar grande demais
    max_width = int(img.width * 0.85)
    wrapped = []
    for line in textwrap.wrap(frase, width=25):
        wrapped.append(line)

    # Calcula altura total
    total_height = sum(draw.textbbox((0, 0), line, font=font_frase)[3] for line in wrapped)
    y_start = (img.height - total_height) / 2 - 50

    # Escreve cada linha centralizada
    for line in wrapped:
        bbox = draw.textbbox((0, 0), line, font=font_frase)
        text_w = bbox[2] - bbox[0]
        x = (img.width - text_w) / 2
        draw.text((x, y_start), line, font=font_frase, fill=(255, 255, 255))
        y_start += bbox[3]

    # Assinatura centralizada embaixo
    assinatura = "@iamjulianocezarh"
    bbox2 = draw.textbbox((0, 0), assinatura, font=font_assinatura)
    sig_w = bbox2[2] - bbox2[0]
    sx = (img.width - sig_w) / 2
    sy = img.height - bbox2[3] - 60

    draw.text((sx, sy), assinatura, font=font_assinatura, fill=(255, 255, 255))

    # Salva imagem
    if not os.path.exists(GENERATED_FOLDER):
        os.makedirs(GENERATED_FOLDER)

    filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    save_path = os.path.join(GENERATED_FOLDER, filename)
    img.save(save_path, quality=95)

    # ===============================
    # NARRATIVA AUTOMÁTICA DA LEGENDA
    # ===============================
    narrativas = [
        "Todo mundo espera coragem para agir, mas a coragem nasce do movimento.",
        "Nada muda enquanto você continua parado. Ação cura medo. Movimento cura dúvida.",
        "A maioria quer resultados, mas poucos querem o processo. Ação é o que separa intenção de transformação.",
        "Você não precisa estar pronto. Precisa começar. O resto se constrói no caminho.",
        "O medo diminui quando você faz o que estava adiando. A ação é sempre o antídoto."
    ]

    narrativa = random.choice(narrativas)

    ctas = [
        "➡ Salve para lembrar depois.",
        "➡ Envie para alguém que precisa despertar.",
        "➡ Me siga: @iamjulianocezarh"
    ]
    cta_text = "\n".join(ctas)

    hashtags_fixas = "#recomeco #motivacao #desenvolvimentopessoal"

    hashtags_ocultas = "\n.\n.\n.\n.\n#mindset #foco #disciplina #superacao #proposito"

    caption = f"{narrativa}\n\n{cta_text}\n\n{hashtags_fixas}{hashtags_ocultas}"

    return save_path, caption


# ==========================================
# UPLOAD PARA CLOUDINARY
# ==========================================
def upload_to_cloudinary(image_path):
    with open(image_path, "rb") as img_file:
        response = requests.post(
            CLOUDINARY_UPLOAD_URL,
            files={"file": img_file},
            data={"upload_preset": os.getenv("CLOUDINARY_UPLOAD_PRESET")}
        )

    result = response.json()
    if "secure_url" not in result:
        raise Exception("Erro ao enviar ao Cloudinary 🚫")

    return result["secure_url"]


# ==========================================
# POSTAR NO INSTAGRAM
# ==========================================
def post_to_instagram(image_url, caption):

    creation = requests.post(
        f"https://graph.facebook.com/v20.0/{INSTAGRAM_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
    ).json()

    if "id" not in creation:
        print("❌ Erro ao criar mídia:", creation)
        raise Exception("Falha ao criar mídia")

    media_id = creation["id"]
    time.sleep(5)

    publish = requests.post(
        f"https://graph.facebook.com/v20.0/{INSTAGRAM_USER_ID}/media_publish",
        data={
            "creation_id": media_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
    ).json()

    return publish


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
def main():
    print("🚀 Gerando imagem e legenda...")
    image_path, caption = create_post_image()

    print("☁ Fazendo upload para Cloudinary...")
    image_url = upload_to_cloudinary(image_path)
    print("✅ Upload concluído:", image_url)

    print("📲 Publicando no Instagram...")
    result = post_to_instagram(image_url, caption)
    print("✅ Publicado:", result)


if __name__ == "__main__":
    main()
