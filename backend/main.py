from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.models_router import router as models_router
from routers.prompts_router import router as prompts_router
from routers.benchmark_route import router as benchmark_router
from services.ollama_services import check_ollama_health
from utils.startup import setup_ollama
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup logic
    setup_ollama()

    yield

    # shutdown logic (optional)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "LLM Benchmarking API running"}

@app.get("/health")
def health():

    ollama_running = check_ollama_health()

    return {
        "backend": "running",
        "ollama": "running" if ollama_running else "not running"
    }

app.include_router(models_router)
app.include_router(prompts_router)
app.include_router(benchmark_router)