from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from telegram.ext import JobQueue
from process import processing_coin_info
from loguru import logger

import requests
import json

# Conversation states
SELECT_NETWORK, TOKEN_ADDRESS, DESCRIPTION = range(3)

dict_network = {
    'ETH':'ethereum',
    'BSC':'bsc'
}

telegram_message_format = """
[{}]({}) \n 
[{}]({}) BUY! \n 
{} \n 
💵 {} ETH (${}) \n 
🔹 [{}](https://etherscan.io/address/{}) | [Txn](https://etherscan.io/tx/{}) \n 
✅ *New Holder* \n 
🔼 Market Cap $*{}* \n 
🦎 [Chart]({})   ✨[Trade]({}) \n 
🦄 [Snipe]({})   🔹[Trending]({}) 
"""

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


    context.job_queue.run_repeating(send_token_info, interval=10, first=0, context=(chat_id, network, token_address, description))

    update.message.reply_text("You will now receive token info every 60 seconds. "
                              "Send /cancel to stop receiving updates.")

    return ConversationHandler.END
    
def send_token_info(context): 
    chat_id, network, token_address, description = context.job.context
    
    network = dict_network.get(network)
    if network == 'ethereum':
        token_url = f'https://dexscreener.com/ethereum/{token_address}'
    base_token_name, base_token_address, quote_token_name, quote_token_address,pair_address, market_cap, pool_id = processing_coin_info(token_url, network)
    token_dict = {
            "base_token_name": base_token_name,
            "base_token_address": base_token_address,
            "quote_token_name":quote_token_name,
            "quote_token_address":quote_token_address,
            "pair_address":pair_address,
            "network": network,
            "market_cap":market_cap,
            "pool_id":pool_id,
            "description":description,
            "token_telegram":token_url,
            "chart":token_url,
            "snipe":token_url,
            "trade":token_url,
            "trending":token_url,
            "ads_text":'ETH TRENDING (LIVE)',
            "ads_url":'https://t.me/cointransactionchannel'
    }
    
    
    response = requests.post('http://localhost:8888/get_last_transaction',data=json.dumps(token_dict)).json()
    if response is not None:
        logger.info('============================ %s' % response['data'])
        for return_dict in response['data']:
            context.bot.send_message(chat_id=chat_id, text=telegram_message_format.format(return_dict['token']['base_token_name'], return_dict['token']['token_telegram'], return_dict['token']['base_token_name'], return_dict['token']['token_telegram'], return_dict['token']['description'],return_dict['eth_value'], return_dict['total_usd'],return_dict['display_from_address'] ,return_dict['from_address'], return_dict['txn'], return_dict['current_market_cap'], return_dict['token']['chart'], return_dict['token']['trade'], return_dict['token']['snipe'], return_dict['token']['trending']), button_text=return_dict['token']['ads_text'], button_url=return_dict['token']['ads_url'])
        
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
