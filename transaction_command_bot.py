from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext
from telegram.ext import JobQueue
import time
# Conversation states
SELECT_NETWORK, TOKEN_ADDRESS, DESCRIPTION = range(3)

dict_network = {
    'ETH':'ethereum',
    'BSC':'bsc'
}

def start(update, context):
    reply_keyboard = [['ETH', 'BSC']]
    update.message.reply_text(
        "Hello! I am TokenInfoBot. Send /cancel at any time to stop.\n"
        "Please select the network:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return SELECT_NETWORK

def received_network(update, context):
    user_choice = update.message.text
    context.user_data['network'] = user_choice

    update.message.reply_text(
        f"Great! You selected {user_choice}. Now, please enter the token address:"
    )

    return TOKEN_ADDRESS

def received_token_address(update, context):
    context.user_data['token_address'] = update.message.text
    update.message.reply_text(
        "Thanks! Now, please enter the token description:"
    )

    return DESCRIPTION

def received_description(update, context):
    context.user_data['description'] = update.message.text
    
    
    chat_id = update.message.chat_id
    
    network = context.user_data['network']
    token_address = context.user_data['token_address']
    description = context.user_data['description']


    context.job_queue.run_repeating(send_token_info, interval=60, first=0, context=(chat_id, network, token_address, description))

    update.message.reply_text("You will now receive token info every 60 seconds. "
                              "Send /cancel to stop receiving updates.")

    return ConversationHandler.END

def send_token_info(context): 
    chat_id, network, token_address, description = context.job.context
    
    token_info_1 = "First piece of token info."
    token_info_2 = "Second piece of token info."

    # Compose the response message
    response_message = (
        f"Network: {network}\n"
        f"Token Address: {token_address}\n"
        f"Description: {description}\n"
        f"Info 1: {token_info_1}\n"
        f"Info 2: {token_info_2}"
    )

    context.bot.send_message(chat_id=chat_id, text=response_message)
    
def cancel(update, context):
    update.message.reply_text("You have unsubscribed from token info updates.", reply_markup=ReplyKeyboardRemove())
    context.chat_data['job_queue'].stop()
    return ConversationHandler.END

def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you obtained from the BotFather
    bot_token = '6668255939:AAGx4pw4yzpQbLqD-PgakV-laF2NhMJWc84'
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    # Create a conversation handler with the states and corresponding functions
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_NETWORK: [MessageHandler(Filters.regex('^(ETH|BSC)$'), received_network)],
            TOKEN_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, received_token_address)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, received_description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
