import random
import os

def get_random_phrase():
    frases_path = os.path.join(os.getcwd(), "frases.txt")

    if not os.path.exists(frases_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {frases_path}")

    with open(frases_path, "r", encoding="utf-8") as f:
        frases = [linha.strip() for linha in f if linha.strip()]

    if not frases:
        raise ValueError("O arquivo frases.txt está vazio!")

    return random.choice(frases)
