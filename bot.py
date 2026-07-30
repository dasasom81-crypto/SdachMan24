import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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

        # deep_translator's detect+translate in one go, with auto source detection
        def translate_sync():
            translator = GoogleTranslator(source="auto", target="en")
            translated_text = translator.translate(text)
            return translated_text

        translated = await loop.run_in_executor(None, translate_sync)

        reply = f"✅ Translation to English:\n{translated}"
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
