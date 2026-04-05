from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
from services.ollama_services import download_model,get_installed_models
from config import TOP_MODELS
import requests
from fastapi import HTTPException

active_downloads = {}

router = APIRouter()

#route to get the models list
@router.get("/models/catalog")
def model_catalog():

    installed_models = get_installed_models()

    # get display names of installed models
    installed_names = [m["name"] for m in installed_models]

    # combine recommended + installed
    all_models = set(TOP_MODELS + installed_names)

    catalog = []

    for model in sorted(all_models):

        full_name = None

        for m in installed_models:
            if m["name"] == model:
                full_name = m["full_name"]
                break

        catalog.append({
            "name": model,                 # UI name
            "full_name": full_name,        # real Ollama name
            "installed": model in installed_names
        })

    return catalog
#route to download a model
@router.post("/models/download")
def download(model: str):
    download_model(model)

    return {"message": f"Downloading {model}..."}

@router.delete("/models/delete")
def delete_model(model: str):

    print("DELETE ROUTE CALLED:", model)

    res = requests.delete(
        "http://localhost:11434/api/delete",
        json={"name": model}
    )

    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete model: {res.text}"
        )

    return {"message": f"{model} deleted successfully"}

@router.get("/models/download-stream")
def download_model_stream(model: str):

    def stream():

        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model},
            stream=True
        )

        active_downloads[model] = response

        try:
            for line in response.iter_lines():

                if not line:
                    continue

                chunk = json.loads(line.decode("utf-8"))
                yield f"data: {json.dumps(chunk)}\n\n"

        except GeneratorExit:
            print(f"Client disconnected: {model}")

        finally:
            # cleanup
            if model in active_downloads:
                del active_downloads[model]

    return StreamingResponse(stream(), media_type="text/event-stream")

@router.post("/models/cancel")
def cancel_download(model: str):

    if model in active_downloads:
        try:
            active_downloads[model].close()
        except:
            pass

        del active_downloads[model]

        return {"message": f"{model} download cancelled"}

    return {"message": "No active download found"}

@router.get("/models/validate")
def validate_model(model: str):

    try:
        res = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model},
            stream=True,
            timeout=10
        )

        for line in res.iter_lines():

            if not line:
                continue

            chunk = json.loads(line.decode("utf-8"))

            # ❌ invalid model
            if "error" in chunk:
                return {"valid": False}

            # ✅ only accept AFTER manifest is confirmed
            if chunk.get("status") == "pulling layers":
                return {"valid": True}

    except Exception:
        return {"valid": False}

    return {"valid": False}

@router.get("/models/gemini")
def list_gemini_models(apiKey: str):

    url = f"https://generativelanguage.googleapis.com/v1/models?key={apiKey}"

    response = requests.get(url)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()

    models = []

    for m in data.get("models", []):
        models.append({
            "name": m.get("name"),
            "methods": m.get("supportedGenerationMethods", [])
        })

    return {
        "models": models
    }