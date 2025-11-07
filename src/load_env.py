from dotenv import load_dotenv
import os

load_dotenv()

print("ACCESS_TOKEN:", os.getenv("ACCESS_TOKEN"))
print("PAGE_ID:", os.getenv("PAGE_ID"))
print("INSTAGRAM_ID:", os.getenv("INSTAGRAM_ID"))
