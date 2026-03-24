import sqlite3
from dotenv import load_dotenv
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import NetworkError
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,ConversationHandler 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is missing in .env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


conn = sqlite3.connect("notices.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    university TEXT,
    email TEXT,
    telegram_id TEXT UNIQUE
)               
""")

conn.commit()
conn.close()

NAME, UNIVERSITY, EMAIL = range(3)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        "Welcome to the University Notice Bot! 🎓\n\nLet's get you set up. What is your name?",
        reply_markup=ReplyKeyboardRemove()
        )
    return NAME

async def ask_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_name = update.message.text
    context.user_data['name'] = user_name
    
    reply_keyboard = [ ['UOM', 'UOV'], ['UOK', 'RUSL'] ]
    
    await update.message.reply_text(
        f"Nice to meet you, {user_name}! Which university do you want notices for?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    
    return UNIVERSITY

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    selected_uni = update.message.text
    context.user_data['university'] = selected_uni
    
    reply_keyboard = [ ['Skip'] ]
    
    await update.message.reply_text(
        "Got it! Finally, if you want email alerts too, type your email address.\n\nIf you only want Telegram alerts, just press 'Skip'.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return EMAIL

async def save_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_email_input = update.message.text
    chat_id = update.message.chat_id
    
    final_name = context.user_data['name']
    final_uni = context.user_data['university']
    
    if user_email_input.lower() == 'skip':
        final_email = None
    else:
        final_email = user_email_input
        
    conn = sqlite3.connect("notices.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO users (id, name, university, email, telegram_id)
    VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?, ?, ?, ?)          
    """, (str(chat_id), final_name, final_uni, final_email, str(chat_id))
    )
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"You are all registered! 🎉\n\nYou will now receive alerts for {final_uni}.",
        reply_markup=ReplyKeyboardRemove()
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text (
        "Setup cancelled. Type /start if you want to try again.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def handle_errors(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, NetworkError):
        logger.warning("Temporary Telegram network issue: %s", context.error)
        return

    logger.exception("Unhandled bot error", exc_info=context.error)

request = HTTPXRequest(
    connect_timeout=10,
    read_timeout=30,
    write_timeout=10,
    pool_timeout=10,
)

app = ApplicationBuilder().token(TOKEN).request(request).build()

conv_handler = ConversationHandler (
    entry_points=[CommandHandler('start', start)], 
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_university)],
        UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_user_data)],
    },
    fallbacks=[CommandHandler('cancel', cancel)] 
)

app.add_handler(conv_handler)
app.add_error_handler(handle_errors)

print("Bot started, waiting for message...")
app.run_polling(
    timeout=30,
    bootstrap_retries=-1,
    drop_pending_updates=False,
)