#!/usr/bin/env python3
"""
recomeco_agent_auto.py
Versão completa: gera artes legíveis (overlay + sombra), monta legenda emocional,
faz upload para Cloudinary e publica no Instagram Graph API.
Modo --test = gera imagem e envia para Cloudinary (não publica).
"""

import os
import sys
import time
import random
import argparse
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import requests
import json

# -----------------------
# Config / Environment
# -----------------------
load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN") or os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
CLOUDINARY_UPLOAD_URL = os.getenv("CLOUDINARY_UPLOAD_URL")
CLOUDINARY_UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_DIR = os.path.abspath(".")
INPUT_IMAGES_DIR = os.path.join(BASE_DIR, "input_images")
POSTED_DIR = os.path.join(BASE_DIR, "postadas")
USED_FILE = os.path.join(BASE_DIR, "used_images.txt")

# Candidate background folders (uses first that exists and has files)
BACKGROUND_FOLDERS = [
    os.path.join(BASE_DIR, "base_images"),
    os.path.join(BASE_DIR, "imagens"),
    os.path.join(BASE_DIR, "images")
]

# Fonts
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
PLAYFAIR = os.path.join(FONTS_DIR, "PlayfairDisplay-Italic.ttf")
FALLBACK_FONT_SIZE = 80

# Ensure folders exist
os.makedirs(INPUT_IMAGES_DIR, exist_ok=True)
os.makedirs(POSTED_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# -----------------------
# Utilidades
# -----------------------
def telegram_notify(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
        requests.post(url, data=data, timeout=10)
    except Exception:
        pass

def safe_load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.load_default()
        except Exception:
            return None

# -----------------------
# Ler frases / fontes externas
# -----------------------
def collect_phrases():
    """
    Procura por várias fontes de frases e retorna uma lista limpa.
    Prioridade: pasta 'frases/' (arquivos .txt), depois arquivos raiz conhecidos.
    """
    frases = []

    # 1) pasta frases/ (uma frase por arquivo ou linhas)
    pasta_frases = os.path.join(BASE_DIR, "frases")
    if os.path.isdir(pasta_frases):
        for fname in sorted(os.listdir(pasta_frases)):
            if fname.lower().endswith(".txt"):
                path = os.path.join(pasta_frases, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        if not text:
                            continue
                        # se arquivo contém múltiplas linhas, cada linha pode ser uma frase
                        lines = [l.strip() for l in text.splitlines() if l.strip()]
                        frases.extend(lines)
                except Exception:
                    continue

    # 2) arquivos raiz conhecidos
    fallback_files = [
        "frases_curta_impacto.txt",
        "frases_assertivas.txt",
        "frases_reflexao.txt",
        "frases.txt",
        "frases_recomeço.json",
        "frases_recomeço.txt",
    ]
    for fname in fallback_files:
        path = os.path.join(BASE_DIR, fname)
        if os.path.exists(path):
            try:
                if path.lower().endswith(".json"):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            frases.extend([str(x).strip() for x in data if str(x).strip()])
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                        frases.extend(lines)
            except Exception:
                continue

    # clean and unique while preserving order
    seen = set()
    out = []
    for s in frases:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out

# -----------------------
# Selecionar background
# -----------------------
def choose_background():
    available = []
    for folder in BACKGROUND_FOLDERS:
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    available.append(os.path.join(folder, f))
    if not available:
        return None
    return random.choice(available)

# -----------------------
# Gerador de imagem com overlay + sombra + assinatura
# -----------------------
def generate_image(phrase: str, output_dir=INPUT_IMAGES_DIR):
    # Escolher background (se não houver, criar fundo simples)
    bg = choose_background()
    if bg:
        try:
            img = Image.open(bg).convert("RGBA")
        except Exception:
            img = Image.new("RGBA", (1080, 1350), (12, 12, 12, 255))
    else:
        img = Image.new("RGBA", (1080, 1350), (12, 12, 12, 255))

    # Redimensionar mantendo proporção para 1080x1350 (padrão IG)
    target_w, target_h = 1080, 1350
    img = img.resize((target_w, target_h), Image.LANCZOS)

    # Escurecer o fundo com overlay (para garantir legibilidade)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * 0.38)))  # ~38% escuro
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Fonte principal (reduz -10% do tamanho base)
    # usamos tamanho dinâmico: frase curta = maior, longa = menor
    base_size = 86  # referência antiga
    # Ajuste de tamanho em função do comprimento
    phrase_len = len(phrase)
    if phrase_len < 40:
        font_size = int(base_size * 0.90)  # -10% global
    elif phrase_len < 90:
        font_size = int(base_size * 0.80)
    else:
        font_size = int(base_size * 0.70)

    font_head = safe_load_font(PLAYFAIR, font_size) or ImageFont.load_default()
    # assinatura menor e também -10%
    font_sign = safe_load_font(PLAYFAIR, int(52 * 0.90)) or ImageFont.load_default()

    # Quebra de texto inteligente: limita largura e usa multiline
    max_width = int(target_w * 0.78)
    words = phrase.split()
    lines = []
    curr = ""
    for w in words:
        test = (curr + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font_head)
        if bbox[2] - bbox[0] <= max_width:
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    # Calcular posição vertical centrada (visualmente um pouco acima)
    line_height = draw.textbbox((0,0), "Ay", font=font_head)[3] - draw.textbbox((0,0), "Ay", font=font_head)[1]
    total_h = line_height * len(lines) + (len(lines) - 1) * int(line_height * 0.25)
    start_y = (target_h - total_h) // 2 - int(line_height * 0.2)  # deslocamento visual

    # Draw text with shadow + stroke for legibility
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_head)
        w = bbox[2] - bbox[0]
        x = target_w // 2
        y = start_y + i * int(line_height * 1.25)

        # Shadow (soft) by drawing offset multiple times with low alpha
        shadow_color = (0, 0, 0, 200)
        # Draw stroke-like shadow by repeating slightly shifted draws
        for ox, oy in ((-2, -2), (-2,2), (2,-2), (2,2)):
            draw.text((x+ox, y+oy), line, font=font_head, fill=shadow_color, anchor="mm")

        # Main white text
        draw.text((x, y), line, font=font_head, fill=(255,255,255,255), anchor="mm")

    # assinatura com sombra leve (na parte inferior)
    sign = "@iamjulianocezarh"
    bbox_s = draw.textbbox((0,0), sign, font=font_sign)
    w_s = bbox_s[2] - bbox_s[0]
    h_s = bbox_s[3] - bbox_s[1]
    x_s = target_w // 2
    y_s = target_h - h_s - 72

    # assinatura sombra
    draw.text((x_s+1, y_s+1), sign, font=font_sign, fill=(0,0,0,200), anchor="mm")
    draw.text((x_s, y_s), sign, font=font_sign, fill=(255,255,255,220), anchor="mm")

    # Converter para RGB antes de salvar (JPEG)
    final = img.convert("RGB")

    # Nome do arquivo
    ts = int(time.time())
    rand = random.randint(1000, 9999)
    filename = f"post_{ts}_{rand}.jpg"
    path_out = os.path.join(output_dir, filename)
    final.save(path_out, format="JPEG", quality=95)

    return path_out

# -----------------------
# Legenda emocional automática (não repete literal a frase)
# -----------------------
HASHTAGS_BASE = [
    "#mentalidade", "#disciplina", "#mindsetbrasil", "#mudança",
    "#crescimento", "#motivacao", "#sucesso", "#foco", "#autoconhecimento"
]

def build_caption(phrase):
    # templates que referenciam a ideia sem repetir
    intros = [
        "Você já percebeu que a transformação começa onde ninguém olha?",
        "Às vezes a hora é menos sobre desejo e mais sobre decisão.",
        "Não espere o mundo mudar: mude sua postura.",
        "A virada começa quando você decide não aceitar o que te corrói.",
        "Essa inquietação que dói é sinal de que algo precisa ser feito."
    ]
    bodies = [
        "A mudança real exige perda, disciplina e coragem. Não é confortável — é necessário.",
        "Parar de tolerar o mínimo é o primeiro passo para ganhar o que realmente importa.",
        "Você não precisa de permissão para ser quem merece ser. A decisão é sua.",
        "Não romantize a dor: entenda-a, transforme-a e saia mais forte do outro lado.",
        "O programa da sua vida só muda quando você escreve novas regras para si mesmo."
    ]
    ctas = [
        "🔗 LINK NA BIO — Conheça o Manual do Recomeço e mude seu ciclo.",
        "🔗 LINK NA BIO — Manual do Recomeço: método prático para quem decide agir.",
        "🔗 LINK NA BIO — Quer entender como virar essa página com propósito?",
    ]

    intro = random.choice(intros)
    body = random.choice(bodies)
    cta = random.choice(ctas)
    hashtags = " ".join(HASHTAGS_BASE + ["#manualdorecomeço"])

    caption = f"{intro}\n\n{body}\n\n{cta}\n\n{hashtags}"
    return caption

# -----------------------
# Upload Cloudinary
# -----------------------
def upload_cloudinary(image_path):
    if not CLOUDINARY_UPLOAD_URL or not CLOUDINARY_UPLOAD_PRESET:
        telegram_notify("❌ Cloudinary não configurado no .env")
        print("❌ Cloudinary não configurado. Defina CLOUDINARY_UPLOAD_URL e CLOUDINARY_UPLOAD_PRESET.")
        return None
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"upload_preset": CLOUDINARY_UPLOAD_PRESET}
            r = requests.post(CLOUDINARY_UPLOAD_URL, files=files, data=data, timeout=60)
        r.raise_for_status()
        resp = r.json()
        url = resp.get("secure_url") or resp.get("url")
        return url
    except Exception as e:
        telegram_notify(f"❌ Erro upload Cloudinary: {e}")
        print("❌ Erro upload Cloudinary:", e)
        return None

# -----------------------
# Instagram API calls
# -----------------------
def create_instagram_media(image_url, caption):
    if not ACCESS_TOKEN or not IG_USER_ID:
        telegram_notify("❌ Instagram credentials missing in .env")
        print("❌ Instagram credentials faltando (.env).")
        return None
    endpoint = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    try:
        r = requests.post(endpoint, data=data, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        telegram_notify(f"❌ Erro criar mídia Instagram: {e}")
        print("❌ Erro criar mídia Instagram:", e)
        if hasattr(e, "response") and e.response is not None:
            try:
                print(e.response.text)
            except Exception:
                pass
        return None

def publish_instagram_media(creation_id):
    endpoint = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    data = {"creation_id": creation_id, "access_token": ACCESS_TOKEN}
    try:
        r = requests.post(endpoint, data=data, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        telegram_notify(f"❌ Erro publicar mídia Instagram: {e}")
        print("❌ Erro publicar mídia Instagram:", e)
        return None

# -----------------------
# Used images bookkeeping
# -----------------------
def mark_image_used(filename):
    try:
        with open(USED_FILE, "a", encoding="utf-8") as f:
            f.write(filename + "\n")
    except Exception:
        pass

# -----------------------
# Main flow
# -----------------------
def pick_phrase_or_fail():
    phrases = collect_phrases()
    if not phrases:
        print("❌ Nenhuma frase encontrada nos arquivos. Coloque frases em 'frases/' ou arquivos fallback.")
        telegram_notify("❌ Nenhuma frase encontrada para postar.")
        return None
    return random.choice(phrases)

def run_once(test_mode=False):
    # 1) pick phrase
    phrase = pick_phrase_or_fail()
    if not phrase:
        return False

    # 2) generate image
    print("🔧 Gerando imagem com frase selecionada...")
    try:
        img_path = generate_image(phrase)
        print("✅ Imagem gerada:", img_path)
    except Exception as e:
        print("❌ Erro ao gerar imagem:", e)
        telegram_notify(f"❌ Erro ao gerar imagem: {e}")
        return False

    # 3) upload to Cloudinary
    print("☁️  Enviando para Cloudinary...")
    url = upload_cloudinary(img_path)
    if not url:
        print("❌ Upload falhou.")
        return False
    print("✔ Imagem enviada para Cloudinary:", url)

    # If test mode: stop here (no publish)
    if test_mode:
        telegram_notify(f"🧪 TEST MODE: imagem enviada para Cloudinary: {url}")
        print("🧪 Test mode: terminado sem publicar.")
        return True

    # 4) build caption
    caption = build_caption(phrase)

    # 5) create media on Instagram
    print("🛰️ Criando mídia no Instagram...")
    resp = create_instagram_media(url, caption)
    if not resp or "id" not in resp:
        print("❌ Falha ao criar mídia:", resp)
        telegram_notify("❌ Falha ao criar mídia no Instagram.")
        return False

    creation_id = resp["id"]
    print("⏳ Mídia criada, id:", creation_id, " — aguardando publicação...")
    time.sleep(6)

    # 6) publish
    pub = publish_instagram_media(creation_id)
    if not pub or "id" not in pub:
        print("❌ Falha ao publicar:", pub)
        telegram_notify("❌ Falha ao publicar mídia no Instagram.")
        return False

    print("✅ Publicado com sucesso! id:", pub.get("id"))
    telegram_notify(f"✅ Post publicado: {img_path}")

    # 7) bookkeeping: move file and mark used
    try:
        base_name = os.path.basename(img_path)
        target = os.path.join(POSTED_DIR, base_name)
        os.replace(img_path, target)
        mark_image_used(base_name)
    except Exception as e:
        print("⚠️ Não consegui mover arquivo:", e)

    return True

# -----------------------
# CLI / Scheduler
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Agente Recomeço - AutoPost")
    parser.add_argument("--test", action="store_true", help="Gera imagem e envia ao Cloudinary, mas não publica no Instagram.")
    parser.add_argument("--once", action="store_true", help="Executa apenas uma vez (sem scheduler).")
    parser.add_argument("--loop", action="store_true", help="Roda em loop de 12h (por padrão inicia 07:00 se --start07 fornecido).")
    parser.add_argument("--start07", action="store_true", help="Se usado com --loop, aguarda até 07:00 para iniciar primeiro post.")
    args = parser.parse_args()

    if args.once or args.test:
        ok = run_once(test_mode=args.test)
        if ok:
            print("✅ Execução finalizada.")
        else:
            print("❌ Execução falhou.")
        return

    if args.loop:
        # optional: wait until 07:00 if requested
        if args.start07:
            print("⏳ Aguardando início às 07:00 para começar o loop...")
            while True:
                now = datetime.now()
                if now.hour == 7 and now.minute == 0:
                    break
                time.sleep(30)
        # loop infinito com intervalo de 12h
        try:
            while True:
                print("▶️ Iniciando ciclo de postagem:", datetime.now().isoformat())
                success = run_once(test_mode=False)
                if not success:
                    print("⚠ Erro nesta rodada. Vou tentar novamente em 12h.")
                print("⏸ Pausando 12 horas...")
                time.sleep(12 * 60 * 60)
        except KeyboardInterrupt:
            print("🛑 Interrompido pelo usuário.")
        return

    # default: run once
    ok = run_once(test_mode=False)
    if ok:
        print("✅ Execução finalizada.")
    else:
        print("❌ Execução falhou.")

if __name__ == "__main__":
    main()
