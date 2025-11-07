"""
generate_post_image.py

Gera imagens de post estilo "RecomeçoIA" automaticamente:
- fundos abstratos escuros (ruído + blur + gradiente + vinheta)
- frases geradas aleatoriamente no seu estilo (PT-BR)
- fonte principal: PlayfairDisplay-Italic.ttf (colocar em fonts/)
- assinatura no rodapé
- salva em generated_posts/

Como usar:
1) Instale dependências:
   pip install pillow numpy
2) Coloque "PlayfairDisplay-Italic.ttf" em fonts/
   (ajuste FONT_MAIN_PATH se necessário)
3) Rode:
   python generate_post_image.py

Ajuste parâmetros no bloco CONFIG abaixo.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import os
import random
import uuid
from datetime import datetime

# -------------------- CONFIG --------------------
IMAGE_SIZE = (1080, 1080)              # (width, height)
OUTPUT_DIR = "generated_posts"
FONTS_DIR = "fonts"
FONT_MAIN_PATH = os.path.join(FONTS_DIR, "PlayfairDisplay-Italic.ttf")
# Se tiver uma fonte sans para a assinatura, coloque aqui. Se não, usa a fonte principal.
FONT_SIG_PATH = os.path.join(FONTS_DIR, "Montserrat-Light.ttf")  # opcional

# estética
BACKGROUND_VARIATION = 0.8   # 0..1, quanto mais alto mais ruído/variação
VIGNETTE_STRENGTH = 0.6     # 0..1
SPOTLIGHT = True

# texto
SIGNATURE = "@iamjulianocezarh"
TEXT_COLOR = (255, 255, 255)
SIG_COLOR = (170, 170, 170)
TEXT_MARGIN = 120           # margem lateral para o bloco de texto
LINE_SPACING = 1.08         # multiplicador do tamanho da linha

# geração
NUM_TRIES = 6               # tentativas para ajustar o tamanho da fonte
# ------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- utilitários de design ----------

def random_seed():
    # Semente aleatória baseada em tempo + uuid para garantir variação
    s = int(datetime.utcnow().timestamp() * 1000) ^ uuid.uuid4().int & 0xffffffff
    random.seed(s)
    np.random.seed(s & 0xffffffff)


def make_abstract_background(size):
    w, h = size
    # gerando ruído base
    noise = np.random.randn(h, w) * 255 * BACKGROUND_VARIATION
    noise = noise.astype(np.uint8)
    img = Image.fromarray(noise, mode="L")

    # aplicar blur pesado para formar nuvens abstratas
    img = img.filter(ImageFilter.GaussianBlur(radius=18))

    # converter para RGB e aplicar gradiente suave vertical (escuro no topo)
    base = Image.new("RGB", (w, h), (10, 10, 10))
    img_rgb = Image.merge("RGB", (img, img, img))
    img_rgb = Image.blend(base, img_rgb, 0.8)

    # gradiente vertical leve (mais claro no centro superior)
    grad = Image.new("L", (1, h))
    for y in range(h):
        # gradiente com foco no terço superior
        pos = y / (h - 1)
        val = int(30 + 180 * (1 - (pos ** 1.6)))
        grad.putpixel((0, y), max(0, min(255, val)))
    grad = grad.resize((w, h))
    grad_rgb = Image.merge("RGB", (grad, grad, grad))
    img_rgb = Image.blend(img_rgb, grad_rgb, 0.28)

    # spotlight no topo central (opcional)
    if SPOTLIGHT:
        spotlight = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(spotlight)
        rx = int(w * 0.25)
        ry = int(h * 0.18)
        x0 = w // 2 - rx
        y0 = int(h * 0.03)
        x1 = w // 2 + rx
        y1 = y0 + ry * 2
        draw.ellipse([x0, y0, x1, y1], fill=255)
        spotlight = spotlight.filter(ImageFilter.GaussianBlur(radius=160))
        spotlight_rgb = Image.merge("RGB", (spotlight, spotlight, spotlight))
        img_rgb = ImageChops = None
        img_rgb = Image.blend(img_rgb, spotlight_rgb, 0.22)

    # vinheta para escurecer bordas
    vign = Image.new("L", (w, h), 255)
    for y in range(h):
        for x in range(w):
            # distância do centro normalizada
            dx = (x - w / 2) / (w / 2)
            dy = (y - h / 2) / (h / 2)
            d = np.sqrt(dx * dx + dy * dy)
            # curva para vinheta
            v = int(255 * (1 - VIGNETTE_STRENGTH * (d ** 2)))
            vign.putpixel((x, y), max(0, min(255, v)))
    img_rgb.putalpha(vign)
    background = Image.new("RGB", (w, h), (0, 0, 0))
    background.paste(img_rgb, (0, 0), img_rgb.split()[-1])

    # pequenas correções: contrast, leve granulação
    background = background.filter(ImageFilter.GaussianBlur(radius=1))
    return background


# ---------- gerador de frases no estilo do projeto ----------

PHRASE_TEMPLATES = [
    "Você acha mesmo que recomeçar é postar frases e chamar isso de cura?",
    "Recomeçar não é apagar. É aprender a lidar com o que ficou.",
    "Curar é aceitar a própria solidão e caminhar com ela.",
    "O silêncio às vezes fala mais alto que qualquer aplauso.",
    "Não confunda movimento com direção.",
    "Quando tudo parece pouco, comece por onde você está.",
]

SUBJECTS = ["Recomeçar", "Curar", "Aceitar", "Silenciar", "Persistir"]
VERBS = ["não é", "exige", "começa com", "aconselha", "revela"]
OBJECTS = [
    "mudar tudo", "aceitar o próprio ritmo", "silenciar para escutar", "seguir sem garantias",
    "usar a dor como mapa", "achar um novo norte"
]

EXTRA_SHORT = [
    "Sem filtro.", "Sem aplausos.", "Com calma.", "Com intenção."
]


def generate_phrase():
    # mistura entre templates conhecidos e frases compostas dinamicamente
    if random.random() < 0.55:
        # escolha uma template pronta
        return random.choice(PHRASE_TEMPLATES)

    # construir dinamicamente
    s = random.choice(SUBJECTS)
    v = random.choice(VERBS)
    o = random.choice(OBJECTS)
    if random.random() < 0.35:
        ext = " " + random.choice(EXTRA_SHORT)
    else:
        ext = ""
    phrase = f"{s} {v} {o}.{ext}"
    # pequenas variações de pontuação
    return phrase


# ---------- funções de texto e layout ----------

def wrap_text(text, draw, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        wsize = draw.textsize(test, font=font)[0]
        if wsize <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text_to_box(draw, text, font_path, box_width, box_height, starting_size=72):
    # tenta reduzir a fonte até caber no box (tentações limitadas)
    size = starting_size
    for i in range(NUM_TRIES):
        font = ImageFont.truetype(font_path, size=size)
        lines = wrap_text(text, draw, font, box_width)
        line_h = font.getsize("A")[1] * LINE_SPACING
        total_h = len(lines) * line_h
        max_line_w = max([draw.textsize(l, font=font)[0] for l in lines]) if lines else 0
        if total_h <= box_height and max_line_w <= box_width:
            return font, lines
        size = int(size * 0.84)
        if size < 18:
            break
    # fallback: return the smallest tested font
    font = ImageFont.truetype(font_path, size=max(size, 16))
    lines = wrap_text(text, draw, font, box_width)
    return font, lines


# ---------- geração final da imagem ----------

def create_post_image(save=True, phrase=None):
    random_seed()
    if phrase is None:
        phrase = generate_phrase()

    img = make_abstract_background(IMAGE_SIZE)
    draw = ImageDraw.Draw(img)
    w, h = IMAGE_SIZE

    # área disponível para o bloco de texto (um retângulo central)
    box_w = w - 2 * TEXT_MARGIN
    box_h = int(h * 0.58)
    # posição do topo do bloco de texto (um pouco acima do centro)
    box_x = TEXT_MARGIN
    box_y = int(h * 0.22)

    # ajustar fonte principal para caber
    if not os.path.exists(FONT_MAIN_PATH):
        raise FileNotFoundError(f"Fonte principal não encontrada: {FONT_MAIN_PATH}")
    font_main, lines = fit_text_to_box(draw, phrase, FONT_MAIN_PATH, box_w, box_h, starting_size=96)

    # calcular posição vertical do bloco para centralizar na área
    line_h = font_main.getsize("A")[1] * LINE_SPACING
    total_h = len(lines) * line_h
    start_y = box_y + max(0, (box_h - total_h) // 2)

    # desenhar cada linha alinhada à esquerda, mas posicionada no centro horizontal da área de texto
    text_x = box_x
    y = start_y
    for line in lines:
        draw.text((text_x, y), line, font=font_main, fill=TEXT_COLOR)
        y += line_h

    # assinatura pequena no rodapé central
    sig_font = None
    if os.path.exists(FONT_SIG_PATH):
        try:
            sig_font = ImageFont.truetype(FONT_SIG_PATH, size=28)
        except Exception:
            sig_font = None
    if sig_font is None:
        sig_font = ImageFont.truetype(FONT_MAIN_PATH, size=26)

    sig_w, sig_h = draw.textsize(SIGNATURE, font=sig_font)
    sig_x = (w - sig_w) // 2
    sig_y = int(h * 0.92) - sig_h
    draw.text((sig_x, sig_y), SIGNATURE, font=sig_font, fill=SIG_COLOR)

    # salvar
    if save:
        fname = datetime.utcnow().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8] + ".jpg"
        out_path = os.path.join(OUTPUT_DIR, fname)
        # salvar com qualidade
        img.save(out_path, quality=92, optimize=True)
        return out_path, phrase
    return None, phrase


# ---------- CLI mínimo ----------
if __name__ == "__main__":
    # gera três imagens de exemplo por execução para testar variações
    n = 1
    for i in range(n):
        path, ph = create_post_image(save=True)
        print("Gerada:", path)
        print("Frase:", ph)

    print("Pronto. As imagens foram salvas em:", OUTPUT_DIR)
