import os
import asyncio
import aiohttp
from datetime import datetime
import json
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")

NEWS_SOURCES = [
    {"name": "Reuters World News", "url": "https://feeds.reuters.com/reuters/worldNews"},
    {"name": "BBC World News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "Associated Press", "url": "https://rss.ap.org/article/APTopHeadlines"},
    {"name": "Deutsche Welle", "url": "https://rss.dw.com/xml/rss-en-world"}
]

SYSTEM_PROMPT = """Esti un analist geopolitic expert. Analizezi stiri din surse credibile despre situatia globala.

Raspunde STRICT in format JSON:
{
  "signal": "BEAR", "BULL" sau "NEUTRAL",
  "intensity": 1-10,
  "context": "2-3 randuri despre ce se intampla, in romana",
  "headline": "titlul stirii principale"
}

BEAR = situatie critica (conflicte, escaladare, instabilitate)
BULL = situatie pozitiva (acorduri, pace, stabilitate)
NEUTRAL = nu sunt stiri geopolitice relevante, totul e linistit, nimic semnificativ de raportat

Daca stirile sunt banale, fara impact geopolitic real, sau nu exista informatii suficiente, foloseste NEUTRAL.
Raspunde DOAR cu JSON, fara text extra, fara backtick-uri."""


class GeopoliticsAnalyzer:
    def __init__(self):
        self.groq_api_key = GROQ_API_KEY

    async def fetch_rss(self, session, source):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; GeopoliticsBot/1.0)"}
            async with session.get(source["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', text)
                    items = []
                    for t in titles[:8]:
                        title = t[0] or t[1]
                        title = re.sub(r'<[^>]+>', '', title).strip()
                        if title and len(title) > 10 and 'RSS' not in title:
                            items.append(title)
                    if items:
                        return f"[{source['name']}]\n" + "\n".join(f"- {item}" for item in items)
        except:
            pass
        return ""

    async def gather_news(self):
        all_news = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rss(session, src) for src in NEWS_SOURCES]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, str) and r:
                    all_news.append(r)
        return "\n\n".join(all_news) if all_news else ""

    async def call_groq(self, news_text):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analizeaza stirile din {datetime.now().strftime('%d %B %Y')}:\n\n{news_text}"}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    data = await resp.json()
                    raw = data["choices"][0]["message"]["content"].strip()
                    raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
                    return json.loads(raw)
        except Exception as e:
            return {"signal": "NEUTRAL", "intensity": 0, "context": "", "headline": ""}

    def format_message(self, analysis, no_news=False):
        signal = analysis.get("signal", "NEUTRAL")
        intensity = int(analysis.get("intensity", 0))
        context = analysis.get("context", "")
        headline = analysis.get("headline", "")
        now = datetime.now().strftime("%H:%M - %d/%m/%Y")

        # NEUTRAL sau no_news
        if signal == "NEUTRAL" or no_news:
            msg = "🤷 Cumetre, n-am ce sa-ti zic\n"
            msg += "─" * 28 + "\n\n"
            msg += "📭 Nimic semnificativ pe plan geopolitic acum.\n"
            msg += "Lumea mai trage un pui de somn...\n\n"
            msg += f"🕐 {now}"
            return msg

        bar = "█" * intensity + "░" * (10 - intensity)

        if signal == "BEAR":
            header = "🔴 Cumetre, creca scade!"
            label = "Tensiune"
        else:
            header = "🚀 Cumetre, urcam pe luna!"
            label = "Impuls pozitiv"

        msg = f"{header}\n{'─'*28}\n\n"
        msg += f"📊 {label}: {bar} {intensity}/10\n\n"
        msg += f"📰 Context:\n{context}\n\n"
        if headline and headline != "N/A":
            hl = headline[:120] + "..." if len(headline) > 120 else headline
            msg += f"🗞 {hl}\n\n"
        msg += f"🕐 {now}"
        return msg

    async def analyze(self):
        news = await self.gather_news()
        if not news:
            return self.format_message({}, no_news=True)
        analysis = await self.call_groq(news)
        return self.format_message(analysis)
