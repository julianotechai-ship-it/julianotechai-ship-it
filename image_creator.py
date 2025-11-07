from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from phrases_generator import get_random_phrase

def create_post_image():
    # Caminhos
    base_image_path = os.path.join("base_images", "background.png")  # coloque seu fundo
    output_path = os.path.join("generated_images", "final.png")
    font_path = os.path.join("fonts", "PlayfairDisplay-Italic.ttf")

    # Carrega imagem
    img = Image.open(base_image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Texto principal
    phrase = get_random_phrase()
    font_main = ImageFont.truetype(font_path, 110)

    # Dimensões
    W, H = img.size

    # Quebra automática de linha
    wrapped_text = textwrap.fill(phrase, width=18)

    # Calcula tamanho do texto
    w, h = draw.multiline_textsize(wrapped_text, font=font_main)

    # Coordenadas (centralizado)
    text_x = (W - w) / 2
    text_y = (H - h) / 2 - 100  # sobe um pouco para não bater no @

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font_main,
        fill=(255, 255, 255),
        align="center"
    )

    # Marca d'água (@)
    watermark = "@iamjulianocezarh"
    font_small = ImageFont.truetype(font_path, 60)
    wm_w, wm_h = draw.textsize(watermark, font=font_small)
    wm_x = (W - wm_w) / 2
    wm_y = H - wm_h - 120  # centralizado no rodapé

    draw.text(
        (wm_x, wm_y),
        watermark,
        font=font_small,
        fill=(255, 255, 255)
    )

    img.save(output_path)
    return output_path

if __name__ == "__main__":
    print("✅ Gerando imagem...")
    path = create_post_image()
    print("✅ Imagem salva em:", path)
