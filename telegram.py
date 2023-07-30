from telegram.ext import Updater
from config import BOT_TOKEN, CHAT_ID

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.bot = Updater(token=self.bot_token, use_context=True)
        self.chat_id = chat_id

    def send_message(self, message):
        self.bot.send_message(chat_id=self.chat_id, text=message)
        
    def start_polling(self):
        self.updater.start_polling()

    def stop_polling(self):
        self.updater.stop()
        
        
a = TelegramBot(BOT_TOKEN, CHAT_ID)
a.send_message('aaa')
        
