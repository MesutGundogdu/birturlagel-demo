# ai-service — Çok-Ajanlı Eşleştirme (referans iskelet)

STRATEJI.md "Katman 2" mimarisinin çalışır iskeleti: **FastAPI + LangGraph + Claude**.

> Bu servis Netlify'da **koşmaz** (statik barındırma). Ayrı bir sunucuda
> (Railway / Fly / AWS) çalışır. Canlı demo şimdilik ya tarayıcı-içi yerel motoru
> ya da `netlify/functions/match.mjs` (tek çağrı Claude) kullanır.

## Akış
```
/match (POST)
  intent → retrieve(pgvector) → reviews(Tripadvisor MCP) → budget → coordinator(Claude) → JSON
```

## Çalıştırma
```bash
cd services/ai
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000
# test:
curl -s localhost:8000/match -H 'content-type: application/json' \
  -d '{"query":"Antalya aile deniz 5 gece 40 bin","hotels":[{"id":"h4","name":"Kalkan Taş Ev","city":"Antalya","price":7200,"sea":true,"family":true,"halal":true}]}'
```

## Sözleşme (ön yüz ile aynı)
İstek: `{ query, hotels:[{id,name,city,price,halal,family,sea,thermal,nature,quiet,urban}] }`
Yanıt: `{ understanding, picks:[{id, score, why}] }`

## Yapılacaklar (üretim)
- `retrieve`: oteli/yorumları embed et, pgvector ile anlamsal benzerlik.
- `reviews`: Tripadvisor MCP aracını bağla (gerçek yorum/fotoğraf).
- `budget`: master-prompt'taki 0-100 ağırlıklı formülün sunucu tarafı.
- Auth, hız sınırı, gözlemlenebilirlik (Sentry/PostHog).
