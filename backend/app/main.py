from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .engine import GameEngine
from .models import CreateGameRequest, LLMConfig, SwitchLLMRequest, VoteRequest

app = FastAPI(title="WolfAI", version="0.1.0")
engine = GameEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/games")
def create_game(req: CreateGameRequest):
    return engine.create_quick_game(req.human_name)


@app.get("/api/games/{game_id}")
def get_game(game_id: str):
    try:
        return engine.get(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="game not found") from exc


@app.post("/api/games/{game_id}/speeches")
def speeches(game_id: str):
    try:
        return engine.generate_day_speeches(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="game not found") from exc


@app.post("/api/games/{game_id}/vote")
def vote(game_id: str, req: VoteRequest):
    try:
        return engine.vote_and_advance(game_id, req.target_player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="game not found") from exc


@app.post("/api/games/{game_id}/llm/switch")
def switch_llm(game_id: str, req: SwitchLLMRequest):
    try:
        config = LLMConfig(
            mode=req.mode,
            provider=req.provider,
            base_url=req.base_url,
            model=req.model or ("llama3" if req.mode == "local" else "qwen-turbo"),
            api_key=req.api_key,
        )
        return engine.switch_llm(game_id, config)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="game not found") from exc


web_root = Path(__file__).resolve().parents[2] / "frontend"
if web_root.exists():
    app.mount("/assets", StaticFiles(directory=web_root), name="assets")


@app.get("/")
def index():
    index_path = web_root / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="frontend not found")
    return FileResponse(index_path)
