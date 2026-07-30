import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create translator
translator = Translator()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! Send me any text in any language, and I'll translate it to English for you instantly."
    )

# Handle messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if not text:
        return

    try:
        await update.message.chat.send_action(action="typing")
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, translator.translate, text, dest='en')
        
        detected_lang = result.src
        translated = result.text

        if detected_lang.lower() == 'en':
            reply = f"📝 This is already English!\n\n{translated}"
        else:
            reply = (
                f"🌐 Detected language: **{detected_lang.upper()}**\n\n"
                f"✅ Translation to English:\n{translated}"
            )
        
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "⚠️ Oops! Something went wrong. Please try again later."
        )

# Main function
def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
