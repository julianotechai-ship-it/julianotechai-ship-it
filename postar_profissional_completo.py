import os
import json
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
CLOUD_URL = os.getenv("CLOUDINARY_UPLOAD_URL")
PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")

FONT_PATH = "fonts/PlayfairDisplay-Italic.ttf"
OUTPUT_DIR = "input_images"
JSON_FRASES = "frases_recomeço.json"

BACKGROUND_COLOR = (10, 10, 10)
TEXT_COLOR = (255, 255, 255)
SIGN_COLOR = (255, 255, 255, 90)

HASHTAGS = "#mentalidade #disciplina #mindsetbrasil #mudança #crescimento #motivacao #sucesso #foco #autoconhecimento #frasesmotivacionais"

# ---------- helpers ----------
def carregar_frases():
    if not os.path.exists(JSON_FRASES):
        print("❌ arquivo frases_recomeço.json não encontrado na raiz do projeto.")
        return []
    with open(JSON_FRASES, "r", encoding="utf-8") as f:
        return json.load(f)

def escolher_frase(frases):
    return random.choice(frases)

def gerar_legenda_profunda(frase):
    """
    Gera uma legenda longa (≈10 linhas) em estilo estoico/provocador
    sem repetir literalmente a 'frase' da imagem.
    Referimos a ideia, expandimos e provocamos ação/emoção.
    """
    # Templates que referenciam a ideia sem repetir palavra-a-palavra
    templates = [
        "Isso é o que corta o conforto pela raiz.",
        "A verdade que incomoda separa quem aceita do que muda.",
        "A escolha que você evita define as próximas décadas da sua vida.",
        "Acomodar-se hoje é pagar com perda de futuro.",
        "Existe um ponto onde a coragem se torna prática diária.",
        "Quem muda postura muda destino; não há atalhos.",
        "Reclamar não transforma — atitude transforma.",
        "A grande virada costuma doer: é o preço da evolução.",
        "Sua nova versão pede renúncia ao velho círculo.",
        "Se não houver ruptura, não haverá avanço real.",
        "A reflexão sem ação vira vitimismo elegante.",
        "O menor gesto repetido com disciplina supera qualquer impulso.",
        "Perder o medo de perder é ganhar liberdade.",
        "Mudar a narrativa interna é mudar o curso da vida.",
        "A dor que você evita é a escola que você falta."
    ]

    # Base: quero 10 linhas. Vamos escolher 9 linhas de templates + 1 CTA no final.
    lines = random.sample(templates, 9)
    # linha final chama para ação/identificação e dá contexto emocional
    cta = "Se isso falou com você, comente 'EU VOU' e comece agora."
    # Monta legenda: não repetir a frase literal. Referimos a ideia com "essa verdade" só se necessário.
    legenda = "\n".join(lines + [cta, "", HASHTAGS])
    return legenda

# ---------- imagem ----------
def criar_imagem(frase):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    img = Image.new("RGBA", (1080, 1350), (*BACKGROUND_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # fontes proporcionais
    tamanho_head = 86
    tamanho_sign = 52
    try:
        font_head = ImageFont.truetype(FONT_PATH, tamanho_head)
        font_sign = ImageFont.truetype(FONT_PATH, tamanho_sign)
    except Exception:
        font_head = ImageFont.load_default()
        font_sign = ImageFont.load_default()

    # quebra inteligente para imagem
    wrapped = textwrap.fill(frase, width=16)

    # calcula bbox e posiciona visualmente um pouco mais alto
    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_head, spacing=6)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (1080 - w) // 2
    y = (1350 - h) // 2 - 40

    draw.multiline_text((x, y), wrapped, fill=TEXT_COLOR, font=font_head, align="center", spacing=6)

    # assinatura com transparência real
    assinatura = "@iamjulianocezarh"
    bbox2 = draw.textbbox((0,0), assinatura, font=font_sign)
    w2 = bbox2[2] - bbox2[0]
    x2 = (1080 - w2) // 2
    y2 = 1350 - 150
    draw.text((x2, y2), assinatura, fill=SIGN_COLOR, font=font_sign)

    final = img.convert("RGB")
    filename = os.path.join(OUTPUT_DIR, f"post_prof_{random.randint(1000,9999)}.jpg")
    final.save(filename, "JPEG", quality=95)
    print("✅ Imagem criada:", filename)
    return filename

# ---------- cloudinary ----------
def upload_cloudinary(caminho):
    with open(caminho, "rb") as f:
        data = {"upload_preset": PRESET}
        files = {"file": f}
        r = requests.post(CLOUD_URL, data=data, files=files)
    try:
        return r.json().get("secure_url")
    except Exception as e:
        print("❌ Erro Cloudinary:", r.text)
        return None

# ---------- instagram ----------
def publicar_instagram(image_url, legenda):
    create_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    payload = {"image_url": image_url, "caption": legenda, "access_token": ACCESS_TOKEN}
    r = requests.post(create_url, data=payload).json()
    print("➡ Criado:", r)
    if "id" not in r:
        print("❌ Falha ao criar mídia")
        return False
    # publish
    publish_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    r2 = requests.post(publish_url, data={"creation_id": r["id"], "access_token": ACCESS_TOKEN}).json()
    print("➡ Publicado:", r2)
    return True

# ---------- fluxo ----------
def executar():
    frases = carregar_frases()
    if not frases:
        return

    frase = escolher_frase(frases)
    # cria imagem com a FRASE escolhida (apenas na imagem)
    caminho = criar_imagem(frase)
    # gera legenda COMPLETAMENTE nova, contextual e sem repetir a frase literalmente
    legenda = gerar_legenda_profunda(frase)
    # upload
    url = upload_cloudinary(caminho)
    if not url:
        print("❌ upload falhou. Abortando.")
        return
    ok = publicar_instagram(url, legenda)
    if ok:
        print("✅ Post pronto.")
    else:
        print("❌ Publicação falhou.")

if __name__ == "__main__":
    executar()
