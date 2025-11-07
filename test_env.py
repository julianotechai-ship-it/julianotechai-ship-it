from dotenv import load_dotenv
import os

load_dotenv()

print("INSTAGRAM_ACCESS_TOKEN:", os.getenv("INSTAGRAM_ACCESS_TOKEN"))
print("IG_USER_ID:", os.getenv("IG_USER_ID"))
print("PAGE_ID:", os.getenv("PAGE_ID"))
