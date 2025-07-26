import os
import time
import openai
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = os.getenv("OWNER_ID")

bot = Bot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

start_time = time.time()
app = FastAPI()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я GPT-бот. Напиши /ask <вопрос> чтобы спросить у ChatGPT.")

# Команда /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - начать
"
        "/ask <вопрос> - задать вопрос GPT
"
        "/uptime - сколько бот работает
"
        "/say <текст> - бот повторит
"
    )

# Команда /uptime
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seconds = int(time.time() - start_time)
    await update.message.reply_text(f"⏱ Uptime: {seconds} секунд")

# Команда /say
async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    await update.message.reply_text(text or "Пусто.")

# Команда /ask (интеграция с OpenAI)
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if OWNER_ID and user_id != OWNER_ID:
        await update.message.reply_text("❌ Доступ запрещён.")
        return

    question = ' '.join(context.args)
    if not question:
        await update.message.reply_text("❗ Напиши вопрос после команды.")
        return

    await update.message.reply_text("✍️ Думаю...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_cmd))
telegram_app.add_handler(CommandHandler("uptime", uptime))
telegram_app.add_handler(CommandHandler("say", say))
telegram_app.add_handler(CommandHandler("ask", ask))

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}

@app.get("/")
def root():
    return {"message": "GPT бот работает"}