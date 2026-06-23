# BirTurlaGel — Demo

AI tabanlı seyahat eşleştirme platformunun **landing sayfası demosu**.

> Bir tur ile gel, bir başka sen ol.

## Hakkında
- **Marka:** BirTurlaGel · an IGO MICE company
- **Tek dosya statik demo:** `index.html`
- **Tasarım sistemi:** Lacivert + Terra Cotta + Altın paleti, Fraunces + Geist tipografisi
- **İçerik kuralları:** Aile dostu, helal konsept, alkolsüz — muhafazakar değerlere saygılı

## Çalışan Özellik — AI Eşleştirme Motoru (prototip)
Sohbet kutusuna doğal dilde yaz (ör. *"Antalya'da çocuklu aile için denize yakın, sessiz, 5 gece, 40 bin TL"*).
Backend olmadan, tamamen tarayıcıda:
1. **Niyet çıkarımı** — bütçe, gece, lokasyon, kişi tipi, ruh hâli, kısıtlar.
2. **Çok kriterli skorlama (0-100)** — ruh hâli %25 · bütçe %20 · kısıt %20 · lokasyon %20 · özellik %10 · yenilik %5.
3. **3 öneri** — her birinde *Neden uygun · Riskler · Kimler için*, sonunda bir *Alternatif*.
4. **Otel detayı** — koleksiyon satırına tıkla → skor kırılımını çubuklarla gör.

> Bu prototip, gerçek çok-ajanlı backend'in (Next.js + FastAPI/LangGraph + Claude) referans spesifikasyonudur.
> Detaylı yol haritası ve 30 reponun sentezi: [`docs/STRATEJI.md`](docs/STRATEJI.md).

### v0.2 — Yeni
- **AI kahraman hero:** koyu, parıltılı, canlı konsol; streaming (typewriter) yanıt; aşamalı "düşünüyor" adımları; **tam ekran** sohbet.
- **Gerçek Claude (opsiyonel):** [`netlify/functions/match.mjs`](netlify/functions/match.mjs). Netlify'da `ANTHROPIC_API_KEY` tanımlanınca site gerçek Claude'a sorar; tanımlı değilse **otomatik yerel motora düşer** (konsoldaki "motor: yerel/Claude" göstergesi).
- **12 otel** koleksiyonu veriden render edilir; her satır tıklanır → skor kırılımı.
- **Çalışan Seyahat DNA testi** (5 soru) — profil grafiğini anında günceller, sonucu sohbete bağlar.
- **Referans backend:** [`services/ai/`](services/ai/) — FastAPI + LangGraph çok-ajanlı iskelet.

#### Gerçek Claude'u açmak
Netlify panel → Site settings → Environment variables → `ANTHROPIC_API_KEY = sk-ant-...` ekle, yeniden deploy et.

## Çalıştırma
Doğrudan `index.html` tarayıcıda açılır. Veya:

```bash
npx serve .
```

## Deploy
Netlify üzerinde otomatik yayında.
