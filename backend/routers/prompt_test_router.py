from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import time
import requests
from config import OLLAMA_URL_GENERATE

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