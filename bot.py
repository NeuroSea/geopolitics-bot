import os
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from analyzer import GeopoliticsAnalyzer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "6"))

analyzer = GeopoliticsAnalyzer()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Bot Geopolitic Activ!\n\n"
        "Comenzi:\n"
        "/check - Analiza imediata\n"
        "/status - Status bot"
    )

async def check_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Analizez situatia globala... un moment!")
    result = await analyzer.analyze()
    await update.message.reply_text(result)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ Bot activ\n"
        f"⏰ Verificare la fiecare {CHECK_INTERVAL_HOURS} ore\n"
        f"🕐 {datetime.now().strftime('%H:%M %d/%m/%Y')}"
    )

async def scheduled_check(context: ContextTypes.DEFAULT_TYPE):
    try:
        result = await analyzer.analyze()
        await context.bot.send_message(chat_id=CHAT_ID, text=result)
        logger.info("Scheduled check trimis cu succes")
    except Exception as e:
        logger.error(f"Eroare scheduled check: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_now))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", start))

    job_queue = app.job_queue
    job_queue.run_repeating(
        scheduled_check,
        interval=CHECK_INTERVAL_HOURS * 3600,
        first=15
    )

    logger.info(f"Bot pornit! Check la fiecare {CHECK_INTERVAL_HOURS} ore.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
