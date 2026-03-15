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