from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

USERS_FILE = "users.json"

TOKEN = os.getenv("BOT_TOKEN")  # توکن از محیط میاد

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    users = load_users()
    users[user_id] = True
    save_users(users)
    await update.message.reply_text("به ربات دانشگاه هنر خوش اومدی!\nیادآوری غذا فعال شد. برای غیرفعال کردن /notify_off رو بفرست.")

async def notify_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    users = load_users()
    users[user_id] = True
    save_users(users)
    await update.message.reply_text("یادآوری غذا فعال شد.")

async def notify_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    users = load_users()
    users[user_id] = False
    save_users(users)
    await update.message.reply_text("یادآوری غذا غیرفعال شد.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("notify_on", notify_on))
app.add_handler(CommandHandler("notify_off", notify_off))
app.run_polling()