import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from pipelines.pipeline_a.naive_pipeline import NaiveRAGPipeline
from pipelines.pipeline_b.hybrid_agent_pipeline import HybridAgenticRAGPipeline
from eval.ragas_engine import RagasEvaluator

DOC_ID_REGEX = re.compile(r"^[A-Z0-9\-]+$")

app = FastAPI(
    title="Clinical Intelligence Benchmark Console",
    description="Clinical Information Retrieval Evaluation",
    version="1.0.0"
)

allowed_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000")
allowed_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

pipeline_a = NaiveRAGPipeline()
pipeline_b = HybridAgenticRAGPipeline()
evaluator = RagasEvaluator()

@app.on_event("startup")
def startup_event():
    try:
        pipeline_a.initialize()
        pipeline_b.initialize()
    except Exception as e:
        pass

class RunRequest(BaseModel):
    query_text: str
    target_pipeline: str = "both"

@app.api_route("/api/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "healthy", "service": "clinical-intelligence-engine"}

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/summary")
def get_summary_metrics():
    metrics_file = PROJECT_ROOT / "eval" / "comparative_metrics.json"
    if not metrics_file.exists():
        raise HTTPException(status_code=404, detail="Comparative metrics not generated yet.")
    with open(metrics_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@app.get("/api/queries")
def get_benchmark_queries():
    benchmark_file = PROJECT_ROOT / "data" / "benchmark" / "gold_benchmark.json"
    if not benchmark_file.exists():
        raise HTTPException(status_code=404, detail="Benchmark queries file not found.")
    with open(benchmark_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@app.get("/api/document/{doc_id:path}")
def get_document_source(doc_id: str):
    clean_id = doc_id.split(",")[0].strip().replace("[", "").replace("]", "")

    if not DOC_ID_REGEX.match(clean_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document identifier format: '{clean_id}'. Expected pattern: '^[A-Z0-9-]+$'."
        )

    corpus_dir = (PROJECT_ROOT / "data" / "corpus").resolve()
    doc_path = (corpus_dir / f"{clean_id}.md").resolve()

    if not doc_path.is_relative_to(corpus_dir):
        raise HTTPException(
            status_code=403,
            detail="Access denied: path traversal attempt detected."
        )

    if not doc_path.exists() or not doc_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Document '{clean_id}' not found in corpus."
        )

    content = doc_path.read_text(encoding="utf-8")
    return {"doc_id": clean_id, "content": content}

@app.post("/api/run")
def run_dual_pipeline(req: RunRequest):
    q = req.query_text.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    resp = {"query": q, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    if req.target_pipeline in ["pipeline_a", "both"]:
        out_a = pipeline_a.query(q, top_k=4)
        resp["pipeline_a"] = out_a

    if req.target_pipeline in ["pipeline_b", "both"]:
        out_b = pipeline_b.query(q)
        resp["pipeline_b"] = out_b

    return JSONResponse(content=resp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=True)
