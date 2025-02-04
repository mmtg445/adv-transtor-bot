import os
import logging
import telebot
import pymongo
from googletrans import Translator
from flask import Flask

# ✅ কনফিগারেশন সেটিংস
API_ID = int(os.getenv("API_ID", "26649585"))
API_HASH = os.getenv("API_HASH", "588a3ea6fd01ae88bd2e10fed7d55b2c")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8013290263:AAGc0aJ-lnUgI-0R2L7S3QSTSXH_d9Sj6sE")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rohanahamed75:gt4RXJZ1mUtOh4Xv@mmtg.0ong5.mongodb.net/?retryWrites=true&w=majority&appName=mmtg)
DEFAULT_LANG = "en"

# ✅ MongoDB সংযোগ
client = pymongo.MongoClient(MONGO_URI)
db = client["translator_bot"]
users_collection = db["users"]

# ✅ টেলিগ্রাম বট সেটআপ
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

# ✅ Flask API হেলথ চেক
app = Flask(__name__)

@app.route('/health')
def health_check():
    return {"status": "running"}, 200

# ✅ ব্যবহারকারীর ভাষা সেটিংস ফাংশন
def get_user_language(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user["language"] if user else DEFAULT_LANG

def set_user_language(user_id, language):
    users_collection.update_one({"user_id": user_id}, {"$set": {"language": language}}, upsert=True)

# ✅ অনুবাদ ফাংশন
def translate_text(text, target_lang):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        logging.error(f"Translation Error: {e}")
        return "⚠️ অনুবাদ করতে সমস্যা হয়েছে!"

# ✅ ভাষা পরিবর্তন বোতাম
@bot.message_handler(commands=['language'])
def choose_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["English", "বাংলা", "हिन्दी", "Español", "Français", "Deutsch"]
    for btn in buttons:
        markup.add(telebot.types.KeyboardButton(btn))
    bot.send_message(message.chat.id, "🌍 আপনার পছন্দের ভাষা নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["English", "বাংলা", "हिन्दी", "Español", "Français", "Deutsch"])
def set_language(message):
    lang_map = {"English": "en", "বাংলা": "bn", "हिन्दी": "hi", "Español": "es", "Français": "fr", "Deutsch": "de"}
    user_id = message.from_user.id
    set_user_language(user_id, lang_map[message.text])
    bot.send_message(message.chat.id, f"✅ আপনার পছন্দের ভাষা সেট করা হয়েছে: {message.text}")

# ✅ বট কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 স্বাগতম! আমি একটি উন্নত অনুবাদক বট। আপনি যেকোনো ভাষায় পাঠিয়ে দিন, আমি অনুবাদ করে দেব!\n\n🔧 ভাষা পরিবর্তন করতে /language ব্যবহার করুন।")

@bot.message_handler(func=lambda message: True)
def translate(message):
    user_id = message.from_user.id
    user_lang = get_user_language(user_id)
    translated_text = translate_text(message.text, user_lang)
    bot.reply_to(message, f"📝 অনুবাদ: {translated_text}")

# ✅ Flask ও টেলিগ্রাম একত্রে চালানো
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(port=5000)).start()
    bot.polling()
