import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


async def save_prompts(file):

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filepath = os.path.join(UPLOAD_DIR, "prompts.txt")

    content = await file.read()

    with open(filepath, "wb") as f:
        f.write(content)

    text = content.decode("utf-8")

    prompts = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    return prompts