// BirTurlaGel — Eşleştirme için Netlify Function (gerçek Claude çağrısı)
// ANTHROPIC_API_KEY ortam değişkeni tanımlıysa çalışır; değilse 503 döner
// ve ön yüz otomatik olarak tarayıcı-içi yerel motora düşer.
import Anthropic from '@anthropic-ai/sdk';

const SYSTEM = `Sen BirTurlaGel'in kişisel seyahat danışmanı yapay zekâsısın.
KURALLAR:
1. ASLA alkol/içki içeren mekân, özellik veya aktivite önerme veya bunlardan bahsetme.
2. Aile dostu / helal / sessiz tercihlerini önceliklendir.
3. YALNIZCA sana verilen otel listesinden seç — liste dışı otel uydurma.
4. En fazla 3 otel öner (seçim paradoksu).
5. Her önerinin NEDEN uygun olduğunu kısa ve kişiselleştirilmiş açıkla.
6. Türkçe yanıt ver.
ÇIKTI: SADECE şu şemada geçerli JSON döndür, başka metin yazma:
{"understanding":"kullanıcının isteğinin tek cümlelik özeti",
 "picks":[{"id":"<otel id>","score":<0-100 uyum>,"why":"<neden uygun, 1-2 cümle>"}]}`;

export const handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method Not Allowed' };

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) {
    // Anahtar yok → ön yüz yerel motora düşsün
    return { statusCode: 503, body: JSON.stringify({ error: 'ANTHROPIC_API_KEY tanımlı değil' }) };
  }

  let body;
  try { body = JSON.parse(event.body || '{}'); }
  catch { return { statusCode: 400, body: JSON.stringify({ error: 'Geçersiz JSON' }) }; }

  const { query, hotels = [] } = body;
  if (!query) return { statusCode: 400, body: JSON.stringify({ error: 'query gerekli' }) };

  const client = new Anthropic({ apiKey: key });
  const userMsg =
    `Kullanıcının isteği: "${query}"\n\n` +
    `Seçebileceğin otel listesi (yalnızca bunlardan seç):\n${JSON.stringify(hotels)}\n\n` +
    `Kurallara uy, en uygun en fazla 3 oteli skorla ve yalnızca JSON döndür.`;

  try {
    const msg = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 1024,
      system: SYSTEM,
      messages: [{ role: 'user', content: userMsg }],
    });
    const text = (msg.content || []).map(b => (b.type === 'text' ? b.text : '')).join('');
    const match = text.match(/\{[\s\S]*\}/);
    const data = JSON.parse(match ? match[0] : text);
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    };
  } catch (e) {
    return { statusCode: 502, body: JSON.stringify({ error: String(e && e.message || e) }) };
  }
};
