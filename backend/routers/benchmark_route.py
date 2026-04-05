from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.benchmark_services import run_benchmark
from services.benchmark_services import load_prompts
from services.benchmark_services import benchmark_model
from schemas.benchmark_schema import BenchmarkRequest
from services.ollama_services import get_installed_models
from config import OLLAMA_URL_GENERATE
import json
import time
import requests
from typing import List
from fastapi import Query

router = APIRouter()

@router.post("/benchmark/run")
def benchmark(request: BenchmarkRequest):
    installed = get_installed_models()

    # split models into valid + invalid
    valid_models = [m for m in request.models if m in installed]
    invalid_models = [m for m in request.models if m not in installed]

    results = []

    if valid_models:
        benchmark_data = run_benchmark(valid_models)

        return {
            "results": benchmark_data["results"],
            "invalid_models": invalid_models,
            "saved_to": benchmark_data["saved_to"]
        }

@router.get("/benchmark/stream")
def stream_benchmark(models: List[str] = Query(...)):

    async def event_stream():

        prompts = load_prompts()

        total_steps = len(models) * len(prompts)
        step = 0

        for model in models:

            total_latency = 0
            total_ttft = 0
            total_tokens = 0

            for prompt in prompts:

                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": True
                }

                start_time = time.time()

                response = requests.post(
                    OLLAMA_URL_GENERATE,
                    json=data,
                    stream=True
                )

                first_token_time = None
                full_text = ""

                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue
                    
                    if first_token_time is None:
                        first_token_time = time.time()

                    if "response" in chunk:
                        full_text += chunk["response"]

                end_time = time.time()

                latency = end_time - start_time
                ttft = first_token_time - start_time if first_token_time else 0
                tokens = len(full_text.split())

                total_latency += latency
                total_ttft += ttft
                total_tokens += tokens

                step += 1
                progress = step / total_steps * 100

                yield f"data: {json.dumps({
                    'model': model,
                    'progress': progress
                })}\n\n"

            avg_latency = total_latency / len(prompts)
            avg_ttft = total_ttft / len(prompts)
            tokens_per_sec = total_tokens / total_latency

            yield f"data: {json.dumps({
                'model': model,
                'avg_latency': avg_latency,
                'avg_ttft': avg_ttft,
                'tokens_per_sec': tokens_per_sec
            })}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/benchmark/api-run")
def benchmark_api(apiKey: str, model: str):

    prompts = load_prompts()

    if not apiKey or not model:
        return {"error": "Missing apiKey or model"}

    # normalize model
    if not model.startswith("models/"):
        model = f"models/{model}"

    results = []

    for prompt in prompts:

        url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={apiKey}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        start_time = time.time()

        response = requests.post(url, json=payload)

        end_time = time.time()

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        try:
            output = data["candidates"][0]["content"]["parts"][0]["text"]
        except:
            output = ""

        latency = end_time - start_time
        tokens = len(output.split())
        tps = tokens / latency if latency > 0 else 0

        results.append({
            "prompt": prompt,
            "latency": latency,
            "tokens": tokens,
            "tokens_per_sec": tps
        })

    avg_latency = sum(r["latency"] for r in results) / len(results)
    total_tokens = sum(r["tokens"] for r in results)
    total_time = sum(r["latency"] for r in results)

    return {
        "model": model,
        "avg_latency": avg_latency,
        "tokens_per_sec": total_tokens / total_time if total_time > 0 else 0,
        "total_tokens": total_tokens,
        "results": results
    }


@router.get("/benchmark/api-stream")
def stream_benchmark_api(apiKey: str, model: str):

    async def event_stream():

        prompts = load_prompts()

        if not model.startswith("models/"):
            model_full = f"models/{model}"
        else:
            model_full = model

        total_steps = len(prompts)
        step = 0

        total_latency = 0
        total_tokens = 0
        total_ttft = 0

        for prompt in prompts:

            url = f"https://generativelanguage.googleapis.com/v1/{model_full}:generateContent?key={apiKey}"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
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

            first_token_time = start_time  # simulated

            end_time = time.time()

            latency = end_time - start_time
            ttft = first_token_time - start_time
            tokens = len(full_text.split())

            total_latency += latency
            total_ttft += ttft
            total_tokens += tokens

            step += 1
            progress = step / total_steps * 100

            yield f"data: {json.dumps({
                'model': model,
                'progress': progress
            })}\n\n"

        avg_latency = total_latency / len(prompts)
        avg_ttft = total_ttft / len(prompts)
        tps = total_tokens / total_latency if total_latency > 0 else 0

        yield f"data: {json.dumps({
            'model': model,
            'avg_latency': avg_latency,
            'avg_ttft': avg_ttft,
            'tokens_per_sec': tps
        })}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/benchmark/unified-run")
def unified_benchmark(request: dict):

    models = request.get("models", [])
    prompts = load_prompts()

    results = []

    for model_info in models:

        provider = model_info.get("provider")
        model_name = model_info.get("name")

        total_latency = 0
        total_tokens = 0
        total_ttft = 0

        for prompt in prompts:

            # -------------------------
            # OLLAMA FLOW
            # -------------------------
            if provider == "ollama":

                data = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True
                }

                start_time = time.time()

                response = requests.post(
                    OLLAMA_URL_GENERATE,
                    json=data,
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

            # -------------------------
            # GEMINI FLOW
            # -------------------------
            elif provider == "gemini":

                api_key = model_info.get("apiKey")

                if not model_name.startswith("models/"):
                    model_name_full = f"models/{model_name}"
                else:
                    model_name_full = model_name

                url = f"https://generativelanguage.googleapis.com/v1/{model_name_full}:generateContent?key={api_key}"

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }

                start_time = time.time()

                response = requests.post(url, json=payload)

                if response.status_code != 200:
                    return {"error": response.text}

                data = response.json()

                try:
                    full_text = data["candidates"][0]["content"]["parts"][0]["text"]
                except:
                    full_text = ""

                first_token_time = start_time  # simulated
                end_time = time.time()

            else:
                return {"error": f"Unknown provider: {provider}"}

            # -------------------------
            # COMMON METRICS
            # -------------------------
            latency = end_time - start_time
            ttft = first_token_time - start_time if first_token_time else 0
            tokens = len(full_text.split())

            total_latency += latency
            total_ttft += ttft
            total_tokens += tokens

        avg_latency = total_latency / len(prompts)
        avg_ttft = total_ttft / len(prompts)
        tps = total_tokens / total_latency if total_latency > 0 else 0

        results.append({
            "model": model_name,
            "provider": provider,
            "avg_latency": avg_latency,
            "avg_ttft": avg_ttft,
            "tokens_per_sec": tps,
            "total_tokens": total_tokens
        })

    return {"results": results}

@router.post("/benchmark/unified-stream")
def unified_benchmark_stream(request: dict):

    models = request.get("models", [])

    async def event_stream():

        prompts = load_prompts()

        total_steps = len(models) * len(prompts)
        step = 0

        for model_info in models:

            provider = model_info.get("provider")
            model_name = model_info.get("name")

            total_latency = 0
            total_ttft = 0
            total_tokens = 0

            for prompt in prompts:

                start_time = time.time()

                # -------------------------
                # OLLAMA
                # -------------------------
                if provider == "ollama":

                    response = requests.post(
                        OLLAMA_URL_GENERATE,
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": True
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

                # -------------------------
                # GEMINI
                # -------------------------
                elif provider == "gemini":

                    api_key = model_info.get("apiKey")

                    if not model_name.startswith("models/"):
                        model_full = f"models/{model_name}"
                    else:
                        model_full = model_name

                    url = f"https://generativelanguage.googleapis.com/v1/{model_full}:generateContent?key={api_key}"

                    response = requests.post(
                        url,
                        json={"contents": [{"parts": [{"text": prompt}]}]}
                    )

                    if response.status_code != 200:
                        yield f"data: {json.dumps({'error': response.text})}\n\n"
                        return

                    data = response.json()

                    try:
                        full_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    except:
                        full_text = ""

                    first_token_time = start_time

                else:
                    yield f"data: {json.dumps({'error': 'Unknown provider'})}\n\n"
                    return

                end_time = time.time()

                latency = end_time - start_time
                ttft = first_token_time - start_time if first_token_time else 0
                tokens = len(full_text.split())

                total_latency += latency
                total_ttft += ttft
                total_tokens += tokens

                step += 1
                progress = step / total_steps * 100

                yield f"data: {json.dumps({
                    'model': model_name,
                    'provider': provider,
                    'progress': progress
                })}\n\n"

            avg_latency = total_latency / len(prompts)
            avg_ttft = total_ttft / len(prompts)
            tps = total_tokens / total_latency if total_latency > 0 else 0

            yield f"data: {json.dumps({
                'model': model_name,
                'provider': provider,
                'avg_latency': avg_latency,
                'avg_ttft': avg_ttft,
                'tokens_per_sec': tps
            })}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")