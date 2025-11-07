from dotenv import load_dotenv
import os

load_dotenv()

print("INSTAGRAM_ID =", os.getenv("INSTAGRAM_ID"))
print("ACCESS_TOKEN =", "OK" if os.getenv("ACCESS_TOKEN") else "NÃO LIDO")
