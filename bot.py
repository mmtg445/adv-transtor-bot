from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator

# Initialize the translator
translator = Translator()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Advanced Translator Bot!\n\n"
        "Send me any text, and I will translate it for you.\n"
        "Use /help to see available commands."
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/translate <text> - Translate text to English\n"
        "/langs - Show supported languages\n"
        "Just send me any text, and I will translate it to English by default!"
    )

# List supported languages
async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    languages = translator.get_supported_languages()
    await update.message.reply_text(
        f"Supported languages:\n\n{', '.join(languages)}"
    )

# Translate text
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        # Detect language and translate to English by default
        translation = translator.translate(text, dest='en')
        await update.message.reply_text(
            f"Translated to English:\n\n{translation.text}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Main function
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    application = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("langs", list_languages))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
