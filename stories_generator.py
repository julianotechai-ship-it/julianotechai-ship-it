import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------
LARGURA = 1080
ALTURA = 1920
PASTA_SAIDA = "input_stories"
FONT_TITULO = "fonts/PlayfairDisplay-Italic.ttf"
FONT_ASSINATURA = "fonts/PlayfairDisplay-Italic.ttf"

os.makedirs(PASTA_SAIDA, exist_ok=True)

# -----------------------------
# CARREGAR PERGUNTAS
# -----------------------------
def carregar_perguntas():
    caminho = "stories_perguntas.txt"
    if not os.path.exists(caminho):
        print("❌ Arquivo stories_perguntas.txt não encontrado. Crie antes de rodar.")
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]
    return linhas

# -----------------------------
# GERAR STORY
# -----------------------------
def gerar_story():
    perguntas = carregar_perguntas()
    if not perguntas:
        return

    pergunta = random.choice(perguntas)

    # Fundo com leve granulação
    img = Image.new("RGB", (LARGURA, ALTURA), color=(12, 12, 12))
    draw = ImageDraw.Draw(img)

    # Texturas leves
    textura = Image.effect_noise((LARGURA, ALTURA), 12)
    textura = textura.convert("RGB").filter(ImageFilter.GaussianBlur(1))
    textura.putalpha(50)
    img.paste(textura, (0, 0), textura)

    # Fonte principal
    fonte = ImageFont.truetype(FONT_TITULO, 70)
    assinatura_font = ImageFont.truetype(FONT_ASSINATURA, 42)

    # CENTRALIZAR A PERGUNTA
    bbox = draw.multiline_textbbox((0, 0), pergunta, font=fonte, spacing=10)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (LARGURA - w) // 2
    y = (ALTURA - h) // 2

    draw.multiline_text((x, y), pergunta, font=fonte, fill=(255, 255, 255), spacing=10, align="center")

    # Assinatura
    assinatura = "@iamjulianocezarh"
    bbox2 = draw.textbbox((0, 0), assinatura, font=assinatura_font)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (LARGURA - w2) // 2
    y2 = ALTURA - h2 - 80
    draw.text((x2, y2), assinatura, font=assinatura_font, fill=(255, 255, 255))

    # Salvar
    nome = f"story_{random.randint(100000, 999999)}.jpg"
    caminho = os.path.join(PASTA_SAIDA, nome)
    img.save(caminho)

    print(f"✅ Story criado: {caminho}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    gerar_story()
