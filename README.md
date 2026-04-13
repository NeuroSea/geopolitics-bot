# 🌍 Bot Geopolitic Telegram

## Deploy pe Railway (recomandat)

### Pasul 1 — Urca codul pe GitHub
1. Mergi pe github.com → New repository → nume: `geopolitics-bot`
2. Descarca GitHub Desktop sau foloseste comenzile:
```bash
cd geopolitics_bot
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/USER/geopolitics-bot.git
git push -u origin main
```

### Pasul 2 — Deploy pe Railway
1. Mergi pe **railway.app** si logheaza-te cu GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Selecteaza repo-ul `geopolitics-bot`
4. Railway detecteaza automat Python si porneste build-ul

### Pasul 3 — Adauga variabilele de mediu
In Railway → proiectul tau → **Variables** → adauga:

| Variabila | Valoare |
|-----------|---------|
| `TELEGRAM_TOKEN` | token-ul de la BotFather |
| `CHAT_ID` | id-ul tau numeric |
| `GROQ_API_KEY` | cheia Groq |
| `CHECK_INTERVAL_HOURS` | `6` |

### Pasul 4 — Redeploy
Dupa ce ai adaugat variabilele → **Deploy** → gata!

---

## Rulare locala
```bash
pip install -r requirements.txt
# Copiaza .env.example in .env si completeaza valorile
cp .env.example .env
python bot.py
```

---

## Comenzi Telegram
| Comanda | Descriere |
|---------|-----------|
| `/check` | Analiza imediata |
| `/status` | Status bot |

## Semnale
- 🔴 **Cumetre, creca scade!** — situatie critica
- 🚀 **Cumetre, urcam pe luna!** — situatie pozitiva
- 🤷 **Cumetre, n-am ce sa-ti zic** — nimic relevant
