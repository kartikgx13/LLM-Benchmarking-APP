from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from config import OLLAMA_URL, OLLAMA_URL_GENERATE
from routers.benchmark_route import unified_benchmark
from services.benchmark_services import PROMPT_FILE, load_prompts, run_benchmark
from services.ollama_services import check_ollama_health, get_installed_models

mcp = FastMCP(name="benchforge-mcp")


@mcp.tool()
def backend_info() -> Dict[str, Any]:
    """Return basic info about this BenchForge MCP server."""
    return {
        "name": "benchforge-mcp",
        "ollama_url": OLLAMA_URL,
        "ollama_generate_url": OLLAMA_URL_GENERATE,
        "prompts_file": PROMPT_FILE,
    }


@mcp.tool()
def ollama_health() -> Dict[str, Any]:
    """Check whether Ollama is reachable."""
    return {"ollama_running": bool(check_ollama_health())}


@mcp.tool()
def list_ollama_models() -> Dict[str, Any]:
    """List installed Ollama models (display + full name)."""
    return {"models": get_installed_models()}


@mcp.tool()
def get_prompts() -> Dict[str, Any]:
    """Return the currently loaded benchmark prompts."""
    prompts = load_prompts()
    return {"count": len(prompts), "prompts": prompts}


@mcp.tool()
def set_prompts(prompts: List[str]) -> Dict[str, Any]:
    """Overwrite prompts file used by benchmarks."""
    cleaned = [p.strip() for p in prompts if isinstance(p, str) and p.strip()]

    # Ensure parent directory exists (uploads/)
    import os

    os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned) + ("\n" if cleaned else ""))

    return {"saved": True, "count": len(cleaned), "prompts_file": PROMPT_FILE}


@mcp.tool()
def run_ollama_benchmark(models: List[str]) -> Dict[str, Any]:
    """
    Run the existing Ollama-only benchmark using prompts.txt.

    Note: This uses `services.benchmark_services.run_benchmark`, which calls Ollama
    with streaming enabled and computes latency/TTFT/tokens/sec across prompts.
    """
    cleaned = [m.strip() for m in models if isinstance(m, str) and m.strip()]
    if not cleaned:
        return {"error": "No models provided"}

    result = run_benchmark(cleaned)
    return result


@mcp.tool()
def run_unified_benchmark(models: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run the existing unified benchmark (ollama/gemini/openrouter) using prompts.txt.

    Each `models[]` item should look like:
    - {"provider":"ollama","name":"llama3"}
    - {"provider":"gemini","name":"gemini-1.5-flash","apiKey":"..."}
    - {"provider":"openrouter","name":"openai/gpt-4.1-mini","apiKey":"..."}
    """
    payload: Dict[str, Any] = {"models": models or []}
    return unified_benchmark(payload)


@mcp.tool()
def test_prompt_ollama(model: str, prompt: str) -> Dict[str, Any]:
    """Quick single-prompt test via Ollama (non-streaming response)."""
    import json
    import time
    import requests

    model = (model or "").strip()
    prompt = (prompt or "").strip()
    if not model or not prompt:
        return {"error": "Missing model or prompt"}

    start_time = time.time()
    resp = requests.post(
        OLLAMA_URL_GENERATE,
        json={"model": model, "prompt": prompt, "stream": True},
        stream=True,
        timeout=60,
    )

    first_token_time: Optional[float] = None
    full_text = ""
    for line in resp.iter_lines():
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
    ttft = (first_token_time - start_time) if first_token_time else 0.0
    tokens = len(full_text.split())
    tps = (tokens / latency) if latency > 0 else 0.0

    return {
        "response": full_text,
        "metrics": {
            "latency": latency,
            "ttft": ttft,
            "tokens": tokens,
            "tokens_per_sec": tps,
        },
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

