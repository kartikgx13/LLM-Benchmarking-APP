import requests
from config import OLLAMA_URL

def get_installed_models():

    res = requests.get(f"{OLLAMA_URL}/api/tags")

    models = res.json()["models"]

    formatted_models = []

    for m in models:

        full_name = m["name"]           # qwen3:latest
        display_name = full_name.split(":")[0]  # qwen3

        formatted_models.append({
            "name": display_name,
            "full_name": full_name
        })

    return formatted_models

def download_model(model):
    requests.post(
        f"{OLLAMA_URL}/api/pull",
        json={"name":model}
    )

def check_ollama_health():
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)

        if res.status_code == 200:
            return True

        return False

    except Exception:
        return False