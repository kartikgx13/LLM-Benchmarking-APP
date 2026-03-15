import requests
import time
import json
import os
import datetime
from config import OLLAMA_URL_GENERATE

# Get backend root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute path to uploads folder
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

#abosulte path to store the results file
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Absolute path to prompts file
PROMPT_FILE = os.path.join(UPLOAD_DIR, "prompts.txt")

def load_prompts():

    if not os.path.exists(PROMPT_FILE):
        print("Prompts file not found:", PROMPT_FILE)
        return []

    with open(PROMPT_FILE, "r") as f:
        prompts = [p.strip() for p in f.readlines() if p.strip()]

    print("Loaded prompts:", prompts)

    return prompts


#model to get the metrics for benchmarking
def benchmark_model(model):

    total_latency = 0
    total_ttft = 0
    total_tokens = 0

    prompts = load_prompts()

    for prompt in prompts:

        data = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        start = time.time()

        response = requests.post(OLLAMA_URL_GENERATE, json=data, stream=True)

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

        end = time.time()

        latency = end - start
        ttft = first_token_time - start if first_token_time else 0
        tokens = len(full_text.split())

        total_latency += latency
        total_ttft += ttft
        total_tokens += tokens

    avg_latency = total_latency / len(prompts)
    avg_ttft = total_ttft / len(prompts)
    tokens_per_sec = total_tokens / total_latency

    return {
        "model": model,
        "avg_latency": avg_latency,
        "avg_ttft": avg_ttft,
        "tokens_per_sec": tokens_per_sec
    }

def run_benchmark(models):

    results = []

    for model in models:

        result = benchmark_model(model)

        results.append(result)
    
    # save results to file
    filepath = save_benchmark_results(results)

    return {
        "results": results,
        "saved_to": filepath
    }

#method to save the benchmark results
def save_benchmark_results(results):

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"benchmark_{timestamp}.json"

    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(results, f, indent=4)

    return filepath