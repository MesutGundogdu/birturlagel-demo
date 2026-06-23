"""
LangGraph çok-ajanlı eşleştirme grafiği (referans iskelet).

Düğümler (Azure-Samples & kbhujbal mimarilerinden uyarlandı):
  intent      → kullanıcının niyetini çıkarır (Claude)
  retrieve    → otel adaylarını filtreler/sıralar (gerçekte pgvector benzerliği)
  reviews     → yorum özeti üretir (gerçekte Tripadvisor MCP aracı)
  budget      → bütçe/skor optimizasyonu
  coordinator → 3 öneriyi NEDEN/RİSK ile JSON'a yazar (Claude)

İçerik kuralı: alkol/uygunsuz içerik hiçbir düğümde üretilmez.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph, END

try:
    from anthropic import Anthropic
except Exception:  # iskelet ortamında SDK yoksa
    Anthropic = None

MODEL = "claude-sonnet-4-6"

SYSTEM = """Sen BirTurlaGel'in seyahat danışmanı AI'ısın.
KURALLAR: alkol/içki içeren hiçbir şey önerme; aile dostu/helal/sessiz tercihlerini
önceliklendir; yalnızca verilen otel listesinden seç; en fazla 3 öneri; Türkçe."""


class MatchState(TypedDict, total=False):
    query: str
    hotels: List[Dict[str, Any]]
    intent: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    understanding: str
    picks: List[Dict[str, Any]]


def _client():
    if Anthropic and os.getenv("ANTHROPIC_API_KEY"):
        return Anthropic()
    return None


# ── Düğümler ────────────────────────────────────────────────────────────────
def node_intent(state: MatchState) -> MatchState:
    """Niyet çıkarımı — gerçekte Claude ile yapılandırılmış çıktı."""
    state["intent"] = {"raw": state["query"]}
    return state


def node_retrieve(state: MatchState) -> MatchState:
    """Aday otelleri getir — gerçekte pgvector kosinüs benzerliği.
    İskelette: tüm listeyi aday kabul eder."""
    state["candidates"] = state.get("hotels", [])
    return state


def node_reviews(state: MatchState) -> MatchState:
    """Yorum özeti — gerçekte Tripadvisor MCP aracı çağrısı.
    İskelette: pas geçer."""
    return state


def node_budget(state: MatchState) -> MatchState:
    """Bütçe/skor optimizasyonu kancası (yer tutucu)."""
    return state


def node_coordinator(state: MatchState) -> MatchState:
    """3 öneriyi Claude ile JSON'a yazar; SDK yoksa basit yedeğe düşer."""
    client = _client()
    hotels = state.get("candidates", [])
    if client is None:
        # Yedek: ilk 3 oteli düz skorla
        state["understanding"] = "İsteğin alındı (yerel yedek)."
        state["picks"] = [
            {"id": h["id"], "score": 80 - i * 3, "why": "Profiline genel uyum."}
            for i, h in enumerate(hotels[:3])
        ]
        return state

    user = (
        f'İstek: "{state["query"]}"\n\nOteller: {json.dumps(hotels, ensure_ascii=False)}\n\n'
        'Yalnızca şu JSON: {"understanding":"...","picks":[{"id":"...","score":0-100,"why":"..."}]}'
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=1024, system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    start, end = text.find("{"), text.rfind("}")
    data = json.loads(text[start:end + 1])
    state["understanding"] = data.get("understanding", "")
    state["picks"] = data.get("picks", [])[:3]
    return state


def build_match_graph():
    g = StateGraph(MatchState)
    g.add_node("intent", node_intent)
    g.add_node("retrieve", node_retrieve)
    g.add_node("reviews", node_reviews)
    g.add_node("budget", node_budget)
    g.add_node("coordinator", node_coordinator)

    g.set_entry_point("intent")
    g.add_edge("intent", "retrieve")
    g.add_edge("retrieve", "reviews")
    g.add_edge("reviews", "budget")
    g.add_edge("budget", "coordinator")
    g.add_edge("coordinator", END)
    return g.compile()
