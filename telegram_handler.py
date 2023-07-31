import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import threading

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=self.bot_token)

        # Add handlers
        self.updater = Updater(token=self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_click))

    def start(self, update, context):
        message_text = "Hello! I'm your Telegram bot. Click the button below to visit our website."

        # Create a button with a link
        keyboard = [[InlineKeyboardButton("Visit our Website", url='https://www.example.com/')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the button
        self.bot.send_message(chat_id=self.chat_id, text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def button_click(self, update, context):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text="Button clicked!")

    def send_message(self, message_text, button_text, button_url):
        # Create a button with the provided text and URL
        keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the button
        self.bot.send_message(chat_id=self.chat_id, text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    def run(self):
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=self.updater.start_polling)
        bot_thread.start()
