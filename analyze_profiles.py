import os
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==== CONFIGURAÇÕES ====
BASE_DIR = "base_images"
OUTPUT_DIR = "output"
FONT_PATH = "arial.ttf"  # pode mudar para outra fonte
WATERMARK = "@manualdorecomeco"
POST_PHRASES = [
    "Nem todo recomeço precisa ser barulhento.",
    "A vida sempre oferece uma segunda chance. Ela se chama hoje.",
    "A força não surge da perfeição, mas da persistência silenciosa.",
    "O recomeço não exige que você esteja pronto, só que você esteja disposto.",
    "Não é sobre vencer o mundo, é sobre não desistir de si mesmo."
]

print("=== RECOMEÇO IA – MODO AUTOMÁTICO ===")

# Escolhe frase
frase = random.choice(POST_PHRASES)

# Escolhe imagem da pasta
images = [f for f in os.listdir(BASE_DIR) if f.lower().endswith((".png",".jpg",".jpeg"))]
if not images:
    raise Exception("⚠ Nenhuma imagem encontrada na pasta base_images!")
img_name = random.choice(images)
img_path = os.path.join(BASE_DIR, img_name)

# Abre imagem e escreve frase
img = Image.open(img_path).convert("RGB")
draw = ImageDraw.Draw(img)

# Carrega fonte
try:
    font = ImageFont.truetype(FONT_PATH, 70)
    wm_font = ImageFont.truetype(FONT_PATH, 40)
except:
    font = ImageFont.load_default()
    wm_font = ImageFont.load_default()

# Posição da frase
w, h = img.size
text_w, text_h = draw.textsize(frase, font=font)
draw.text(((w-text_w)/2, h*0.25), frase, font=font, fill=(255,255,255))

# Marca d’água
wm_w, wm_h = draw.textsize(WATERMARK, font=wm_font)
draw.text((w-wm_w-30, h-wm_h-30), WATERMARK, font=wm_font, fill=(255,255,255))

# Salva imagem
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

output_file = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
save_path = os.path.join(OUTPUT_DIR, output_file)
img.save(save_path)

print(f"✅ Imagem gerada: {save_path}")

# ---- LEGENDAR ----
caption = (
    f"{frase}\n\n"
    "A vida não exige que suportemos tudo com força, "
    "mas com coragem. Cada passo silencioso que você dá "
    "em direção ao que acredita já é vitória. "
    "Recomeços não são sinal de fraqueza — são sinal de vida. "
    "Porque quem ainda tenta, ainda acredita.\n\n"
    "Siga em frente. 🌙"
)

# ---- UPLOAD PRO Instagram ----
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
PAGE_ID = os.getenv("IG_USER_ID")

if not ACCESS_TOKEN or not PAGE_ID:
    raise Exception("⚠ IG_ACCESS_TOKEN e IG_USER_ID não encontrados no .env")

# 1 - Upload para imgbb
print("➡ Enviando imagem para ImgBB...")
with open(save_path, "rb") as f:
    r = requests.post("https://api.imgbb.com/1/upload", data={"key": os.getenv("IMGBB_KEY")}, files={"image": f})
res = r.json()
img_url = res["data"]["url"]
print("✅ Imagem hospedada")

# 2 - Criar mídia no Instagram
print("➡ Criando mídia no Instagram...")
create_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/media"
payload = {
    "image_url": img_url,
    "caption": caption,
    "access_token": ACCESS_TOKEN
}
create_res = requests.post(create_url, data=payload).json()

if "id" not in create_res:
    print("❌ Erro ao criar mídia:", create_res)
    exit()

creation_id = create_res["id"]

# 3 - Publicar
print("➡ Publicando...")
publish_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/media_publish"
publish_res = requests.post(publish_url, data={
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN
}).json()

if "id" in publish_res:
    print("✅ PUBLICADO COM SUCESSO!")
else:
    print("❌ Erro ao publicar:", publish_res)
