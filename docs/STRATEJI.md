# BirTurlaGel — Strateji & Yol Haritası
### 30 GitHub reposunun sentezi → bizim sitede ne yapılacak

> Bu doküman, Hermes araştırmasında çıkarılan 30 AI-seyahat reposunu inceleyip,
> bizim mevcut demoda **neyin eksik olduğunu** ve **neyi nasıl inşa edeceğimizi** sabitler.
> Tek cümlelik hedef: *Booking listeler; biz karar veririz.*

---

## 1. 30 Repodan Çıkan Kritik Notlar

İncelenen 30 repo dağınık görünse de **3 net mimari katmana** ayrışıyor. Hepsinde tekrar eden ortak kalıplar:

### A. Tekrar eden mimari (referans alınacak)
| Katman | Hangi repolar gösteriyor | Bizim için ders |
|--------|--------------------------|-----------------|
| **Niyet çıkarımı (NLU)** | hardikverma22/travel-planner-ai, zinedkaloc/ai-travel-planner, JianXiao2021/travel_agent_LLM | Kullanıcı serbest metin yazar → lokasyon, bütçe, tarih, kişi tipi, ruh hali, kısıt çıkarılır. **Form değil, sohbet.** |
| **Çok-ajanlı orkestrasyon** | Azure-Samples/azure-ai-travel-agents, kbhujbal/Multi-Agent-AI-Travel-Advisor, Haohao-end/Ctrip-Style, shaheennabi/Production-Ready-TripPlanner, sourangshupal/Trip-Planner-CrewAI | "Tek dev prompt" yerine uzman ajanlar: otel-ajanı, bütçe-ajanı, yorum-ajanı, rota-ajanı. Her biri kendi işini yapıp koordinatöre döner. |
| **RAG + vektör arama** | NJUxlj/Travel-Agent-Qwen2-RLHF, jonathanscholtes/Travel-AI-Agent-Cosmos-Vector, alexlmoney83/travel-planning-agent, aws-samples/personalized-travel-itinerary | Otel/yorum verisi embed edilip vektör DB'ye konur; "sessiz + termal + aile" gibi anlamsal sorgu benzerlikle eşleşir. **pgvector/Pinecone** bizim master-prompt'ta zaten var. |
| **Dış veri (MCP/tool-calling)** | pab1it0/tripadvisor-mcp, MikkoParkkola/trvl, SWUSTcyt/langchain-travel-agent | Otel yorumu, fotoğraf, fiyat, hava durumu, POI canlı API'lerden gelir. MCP standardı 2026'da olgunlaşmış — **entegrasyon katmanını MCP üstüne kur.** |
| **Çok kriterli skorlama** | sachinnpraburaj/Intelligent-Travel-Recommendation, shr1911/Tourism-Recommendation, Diivvuu/ai-trip-planner | Sıralama **fiyata göre değil**, uygunluk skoruna göre. Kişilik + bütçe + yorum + lojistik ağırlıklı. Bu bizim master-prompt'taki 0-100 formülün ta kendisi. |

### B. Lisans gerçeği (ticari kullanım)
- **Güvenle baz alınabilir (MIT / MIT-0):** Azure-Samples, kbhujbal, pab1it0/tripadvisor-mcp, aws-samples, jonathanscholtes, sourangshupal, satendra03/Journey-Jolt.
- **"Lisans yok" olanlar** (çoğunluk): kod kopyalanmaz — yalnızca **mimari ve akış** öğrenmek için.
- **GPL-3.0** (AdritPal08): bulaşıcı lisans, ticari kapalı üründe **kaçınılır**.

### C. Teknoloji seçimi sinyali
- Backend AI için ekosistem **Python (LangGraph/CrewAI/LlamaIndex)** etrafında yoğunlaşmış; en kurumsal örnek (Azure) ise **TypeScript + MCP**.
- Bizim master-prompt **Next.js + Vercel AI SDK + @anthropic-ai/sdk** diyor → TypeScript hattı doğru ve Azure örneğiyle hizalı. **AI servisini ayrı (FastAPI) tutma opsiyonu** LangGraph repolarıyla uyumlu.

---

## 2. Bizim Sitenin Durumu — Boşluk Analizi

Mevcut `index.html` **görsel olarak güçlü** (editorial dergi, tutarlı tasarım dili) ama **işlevsel olarak %100 statik**:

| Bölüm | Şu an | Sorun |
|-------|-------|-------|
| AI Sohbeti | Sabit 2 balon, sahte | **Kalp özellik çalışmıyor.** Ürünün tüm vaadi bu. |
| Otel Koleksiyonu | 6 satır, tıklanamaz | Uyum skoru var ama "neden 94?" açıklaması yok. |
| Seyahat DNA | Sabit yüzdeler | Test yok, etkileşim yok. |
| Arama Modları | Dekoratif kartlar | Tıklayınca bir şey olmuyor. |
| Skor mantığı | Yok | Hermes'in dediği farklılaştırıcı (Neden/Risk/Kim için/Alternatif) hiç yok. |

**Sonuç:** Site bir *afiş*. Hermes'in işaret ettiği ürün ise bir *karar motoru*. Aradaki köprü kurulmalı.

---

## 3. Seçtiğim Yapı (Karar)

Statik Netlify barındırması ve API anahtarı olmadan **bugün çalışan** bir şey teslim etmek için iki katmanlı yaklaşım:

### Katman 1 — ŞİMDİ (bu commit): Tarayıcı-içi Eşleştirme Motoru (prototip)
Backend'siz, gerçek çalışan bir demo. 30 repodan damıtılan **çok kriterli skorlama + niyet çıkarımı + 3-öneri açıklaması** kalıbını saf JS ile uygular:

1. **Niyet ayrıştırıcı:** Serbest Türkçe metin → `{bütçe, gece, lokasyon, kişiTipi, ruhHali[], kısıtlar[]}`.
2. **Skor motoru (0-100):** master-prompt formülünün hafif sürümü —
   ruh-hali uyumu %30 · bütçe %20 · kısıt (helal/aile/sessiz) %20 · lokasyon %15 · özellik %10 · yenilik %5.
3. **3-öneri çıktısı** (Hermes formatı): her otel için **Neden uygun · Riskler · Kimler için · Alternatif**.
4. **Otel detayı + skor kırılımı:** koleksiyon satırına tıkla → skorun neden o olduğu çubuklarla açılır.
5. **İçerik kuralı:** alkol/uygunsuz içerik motorun veri setinde ve çıktısında **yok**; helal/aile/sessiz öncelikli.

> Bu, demoyu "afiş"ten "deneyimlenebilir ürün"e taşır ve yatırımcıya/partnere **mantığı gösterilebilir** hale getirir.

### Katman 2 — SONRA (gerçek backend): Çok-ajanlı sistem
Master-prompt + Azure/kbhujbal mimarisi:
- **Next.js (web)** + **FastAPI ai-service** (LangGraph orkestrasyon).
- Ajanlar: `niyet-ajanı → otel-arama (pgvector) → yorum-özet (Tripadvisor MCP) → bütçe-optimizasyon → koordinatör`.
- **Claude (Opus 4.x)** üzerinden çıktı; veri **PostgreSQL+pgvector**, yorum/fiyat **MCP** araçları.
- Bugün yazdığımız niyet+skor mantığı, backend'in **referans spesifikasyonu** olur (boşa gitmez).

---

## 4. HEDEF (net teslim tanımı)

**Bu turun hedefi — TAMAMLANDI sayılır ise:**
> Kullanıcı sohbet kutusuna *"Antalya'da çocuklu aile için denize yakın, sessiz, kahvaltılı, 5 gece, bütçem 40 bin TL"* yazınca; site, gerçek bir skorlama yapıp **uygunluk sırasına göre 3 otel** döndürür — her birinde **Neden uygun / Riskler / Kimler için**, sonunda **bir alternatif**. Koleksiyondaki her otel tıklanıp **skor kırılımı** görülebilir. Tüm akış statik Netlify'da, backend'siz çalışır ve GitHub'a push edilir.

**Sonraki turun hedefi (öneri):**
> ai-service iskeleti (FastAPI + LangGraph) + Claude bağlantısı + 12 otelin pgvector'e gömülmesi; tarayıcı motoru gerçek API'ye bağlanır.

---

## 5. Önceliklendirilmiş Repo Kısa Listesi (bizim için)
1. **Azure-Samples/azure-ai-travel-agents** — ana mimari iskelet (MIT, TS, MCP).
2. **kbhujbal/Multi-Agent-AI-Travel-Advisor** — ajan rolleri ve tool-calling (MIT).
3. **pab1it0/tripadvisor-mcp** — yorum/fotoğraf veri bağlantısı (MIT).
4. **jonathanscholtes/Travel-AI-Agent-Cosmos-Vector** — vektör arama + booking akışı (MIT).
5. **aws-samples/personalized-travel-itinerary-planner** — kişiselleştirme mimarisi (MIT-0).

*"Lisans yok" repolar yalnızca fikir/akış için; kod taşınmaz.*
