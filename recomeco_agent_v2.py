import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import requests
import cloudinary
import cloudinary.uploader
import time

# ✅ Carrega variáveis do .env
load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# ✅ Configura Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# ✅ Caminhos
BASE_IMG = "base_images/base.png"
OUTPUT_IMG = f"generated_images/final.png"
FONT_PATH = "fonts/PlayfairDisplay-Italic.ttf"


def gerar_imagem(texto="Você renasce toda vez que decide recomeçar."):
    print("➡️ Gerando imagem...")

    img = Image.open(BASE_IMG).convert("RGBA")
    draw = ImageDraw.Draw(img)

    try:
