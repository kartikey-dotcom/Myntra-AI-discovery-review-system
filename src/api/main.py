"""
FastAPI Server for Myntra Growth Intelligence | VoC Discovery Engine.
Serves static frontend dashboard and REST endpoints for data exploration & LLM connectivity.
"""

import os
import sys
import json
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.llm_client import LLMClient

app = FastAPI(title="Myntra VoC Growth Intelligence Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(WORKSPACE_ROOT, "frontend")
DATA_DIR = os.path.join(WORKSPACE_ROOT, "data")
ENV_FILE = os.path.join(WORKSPACE_ROOT, ".env")

llm_client = LLMClient()

class KeyConfigRequest(BaseModel):
    provider: str = "gemini"
    api_key: str
    model_name: Optional[str] = None

class LLMQueryRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    api_key: Optional[str] = None
    system_instruction: Optional[str] = None

# Mount frontend directory for static assets
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def get_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/styles.css")
def get_styles():
    return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"))

@app.get("/app.js")
def get_app_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "app.js"))

@app.get("/data/classification_summary.json")
def get_summary_data():
    summary_path = os.path.join(DATA_DIR, "classification_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"error": "Summary not found"})

@app.get("/data/ranked_opportunity_matrix.json")
def get_opportunity_data():
    opp_path = os.path.join(DATA_DIR, "ranked_opportunity_matrix.json")
    if os.path.exists(opp_path):
        with open(opp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"error": "Opportunity matrix not found"})

@app.get("/data/classified_corpus_15k.json")
def get_classified_records():
    rec_path = os.path.join(DATA_DIR, "classified_corpus_15k.json")
    if os.path.exists(rec_path):
        with open(rec_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"error": "Classified corpus not found"})

@app.get("/Part_1_to_7_NextLeap_Deliverables.md")
def get_deliverables_md():
    deliv_path = os.path.join(WORKSPACE_ROOT, "Part_1_to_7_NextLeap_Deliverables.md")
    if os.path.exists(deliv_path):
        return FileResponse(deliv_path, media_type="text/markdown")
    return JSONResponse(status_code=404, content={"error": "Deliverables not found"})

# ==================== LLM INTEGRATION ENDPOINTS ====================

@app.get("/api/v1/llm/status")
def get_llm_status():
    global llm_client
    return {
        "configured": llm_client.is_configured(),
        "provider": llm_client.provider,
        "model_name": llm_client.model_name
    }

@app.post("/api/v1/llm/test-connection")
def test_llm_connection(req: KeyConfigRequest):
    tester = LLMClient(provider=req.provider, api_key=req.api_key, model_name=req.model_name)
    result = tester.test_connection()
    return result

@app.post("/api/v1/llm/save-key")
def save_llm_key(req: KeyConfigRequest):
    global llm_client
    # Update active environment and client
    if req.provider.lower() == "gemini":
        os.environ["GEMINI_API_KEY"] = req.api_key
    else:
        os.environ["OPENAI_API_KEY"] = req.api_key
    os.environ["LLM_PROVIDER"] = req.provider.lower()
    if req.model_name:
        os.environ["LLM_MODEL_NAME"] = req.model_name

    # Write to .env file
    lines = [
        f"LLM_PROVIDER={req.provider.lower()}",
        f"GEMINI_API_KEY={req.api_key if req.provider.lower() == 'gemini' else os.getenv('GEMINI_API_KEY', '')}",
        f"OPENAI_API_KEY={req.api_key if req.provider.lower() == 'openai' else os.getenv('OPENAI_API_KEY', '')}",
        f"LLM_MODEL_NAME={req.model_name or ('gemini-1.5-flash' if req.provider.lower() == 'gemini' else 'gpt-4o-mini')}",
        "LLM_TEMPERATURE=0.2"
    ]
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    llm_client = LLMClient(provider=req.provider, api_key=req.api_key, model_name=req.model_name)
    return {"status": "SUCCESS", "message": f"{req.provider.upper()} API Key saved and activated successfully."}

@app.post("/api/v1/llm/query")
def run_llm_query(req: LLMQueryRequest):
    global llm_client
    active_client = llm_client
    if req.api_key:
        active_client = LLMClient(provider=req.provider or "gemini", api_key=req.api_key)

    if not active_client.is_configured():
        return JSONResponse(
            status_code=400,
            content={"error": "LLM API Key is not configured. Please connect your Gemini or OpenAI key in settings."}
        )

    sys_inst = req.system_instruction or (
        "You are an AI Fashion Growth Advisor for Myntra. "
        "Answer questions strictly grounded in the analyzed 15,000 VoC customer reviews. "
        "Do NOT suggest monetary discounts or sale markdowns. Provide purely visual, styling, or UX solutions."
    )

    response_text = active_client.generate_text(req.prompt, sys_inst)
    return {
        "provider": active_client.provider,
        "model": active_client.model_name,
        "response": response_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
