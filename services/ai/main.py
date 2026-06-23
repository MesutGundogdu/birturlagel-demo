"""
BirTurlaGel — ai-service (referans iskelet)
============================================
FastAPI + LangGraph çok-ajanlı eşleştirme servisi.

Bu, STRATEJI.md'deki "Katman 2" mimarisinin çalışır iskeletidir:
  niyet-ajanı → otel-arama (pgvector) → yorum-özet (MCP) → bütçe-optimizasyon → koordinatör

NOT: Bu dosya Netlify'da KOŞMAZ (statik barındırma). Ayrı bir sunucuda
(Railway/Fly/AWS) çalışır; ön yüz buraya /match ile bağlanır.

Çalıştırma:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph import build_match_graph

app = FastAPI(title="BirTurlaGel ai-service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # üretimde birturlagel domainleriyle sınırla
    allow_methods=["*"],
    allow_headers=["*"],
)

# İçerik kuralı: alkol/uygunsuz içerik tüm akışta yasaktır (bkz. graph.py system prompt).
GRAPH = build_match_graph()


class Hotel(BaseModel):
    id: str
    name: str
    city: str
    price: int
    halal: bool = False
    family: bool = False
    sea: bool = False
    thermal: bool = False
    nature: bool = False
    quiet: bool = False
    urban: bool = False


class MatchRequest(BaseModel):
    query: str
    hotels: List[Hotel] = []


class Pick(BaseModel):
    id: str
    score: int
    why: str


class MatchResponse(BaseModel):
    understanding: str
    picks: List[Pick]
    source: str = "ai-service"


@app.get("/health")
def health() -> dict:
    return {"ok": True, "has_key": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.post("/match", response_model=MatchResponse)
def match(req: MatchRequest) -> MatchResponse:
    """Kullanıcının doğal dil isteğini çok-ajanlı grafikten geçirir."""
    state = GRAPH.invoke({
        "query": req.query,
        "hotels": [h.model_dump() for h in req.hotels],
    })
    return MatchResponse(
        understanding=state.get("understanding", ""),
        picks=[Pick(**p) for p in state.get("picks", [])][:3],
    )
