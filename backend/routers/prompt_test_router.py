from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import time
import requests
from config import OLLAMA_URL_GENERATE
from services.benchmark_services import load_prompts

router = APIRouter()

@router.post("/prompt/test")
def test_prompt(data: dict):
    model = data.get("model")
    prompt = data.get("prompt")

    start_time = time.time()

    response = requests.post(
        OLLAMA_URL_GENERATE,
        json={
            "model":model,
            "prompt":prompt,
            "stream":True
        },
        stream=True
    )

    first_token_time = None
    full_text = ""

    for line in response.iter_lines():
        if not line:
            continue

        try:
            chunk = json.loads(line.decode("utf-8"))
        except:
            continue

        if first_token_time is None:
            first_token_time = time.time()

        if "response" in chunk:
            full_text += chunk["response"]

    end_time = time.time()

    latency = end_time - start_time
    ttft = first_token_time - start_time if first_token_time else 0
    tokens = len(full_text.split())
    tps = tokens / latency if latency > 0 else 0

    return {
        "response": full_text,
        "metrics": {
            "latency": latency,
            "ttft": ttft,
            "tokens_per_sec": tps,
            "tokens": tokens
        }
    }

@router.get("/prompt/test-stream")
def test_prompt_stream(model: str, prompt: str):

    def generate():

        start_time = time.time()
        first_token_time = None
        full_text = ""

        response = requests.post(
            OLLAMA_URL_GENERATE,
            json={
                "model": model,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )

        for line in response.iter_lines():

            if not line:
                continue

            try:
                chunk = json.loads(line.decode("utf-8"))
            except:
                continue

            if first_token_time is None:
                first_token_time = time.time()

            if "response" in chunk:
                token = chunk["response"]
                full_text += token

                yield f"data: {json.dumps({'token': token})}\n\n"

        # metrics at end
        end_time = time.time()

        latency = end_time - start_time
        ttft = first_token_time - start_time if first_token_time else 0
        tokens = len(full_text.split())
        tps = tokens / latency if latency > 0 else 0

        yield f"data: {json.dumps({'done': True, 'metrics': {
            'latency': latency,
            'ttft': ttft,
            'tokens_per_sec': tps,
            'tokens': tokens
        }})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/prompt/test-api")
def test_prompt_api(data: dict):
    api_key = data.get("apiKey")
    model = data.get("model")  # e.g. "gemini-1.5-flash"
    prompt = data.get("prompt")

    if not api_key or not model or not prompt:
        return {"error": "Missing apiKey, model or prompt"}

    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    start_time = time.time()

    response = requests.post(url, json=payload)

    end_time = time.time()

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()

    # extract text safely
    try:
        output = data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        output = "No response"

    latency = end_time - start_time
    tokens = len(output.split())
    tps = tokens / latency if latency > 0 else 0

    return {
        "response": output,
        "metrics": {
            "latency": latency,
            "tokens_per_sec": tps,
            "tokens": tokens
        }
    }

@router.get("/prompt/test-api-stream")
def test_prompt_api_stream(apiKey: str, model: str, prompt: str):

    def generate():

        # normalize model name
        if not model.startswith("models/"):
            model_full = f"models/{model}"
        else:
            model_full = model

        url = f"https://generativelanguage.googleapis.com/v1/{model_full}:generateContent?key={apiKey}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        start_time = time.time()

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            yield f"data: {json.dumps({'error': response.text})}\n\n"
            return

        data = response.json()

        try:
            full_text = data["candidates"][0]["content"]["parts"][0]["text"]
        except:
            full_text = ""

        first_token_time = None

        # 🔥 simulate streaming token by token
        words = full_text.split()

        for word in words:
            if first_token_time is None:
                first_token_time = time.time()

            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            time.sleep(0.02)  # small delay for realism

        end_time = time.time()

        latency = end_time - start_time
        ttft = first_token_time - start_time if first_token_time else 0
        tokens = len(words)
        tps = tokens / latency if latency > 0 else 0

        yield f"data: {json.dumps({
            'done': True,
            'metrics': {
                'latency': latency,
                'ttft': ttft,
                'tokens_per_sec': tps,
                'tokens': tokens
            }
        })}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

