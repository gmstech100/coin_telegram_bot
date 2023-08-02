from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext
from telegram.ext import JobQueue
from process import processing_coin_info
from config import GET_TRADE_HISTORY, INFURA_ID, CONVERT_USD_ETH
from transaction import EthereumTransaction
from token_socket import read_socket
from loguru import logger
import aiohttp
import json
import asyncio
from database import database
from bot import usd_to_eth

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


    context.job_queue.run_repeating(send_token_info, interval=10, first=0, context=(chat_id, network, token_address, description))

    update.message.reply_text("You will now receive token info every 60 seconds. "
                              "Send /cancel to stop receiving updates.")

    return ConversationHandler.END

async def process_get_transaction_by_token(network, token_address, description):
    network = dict_network.get(network)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
    }
    token_url = ''
    if network == 'ethereum':
        token_url = f'https://dexscreener.com/ethereum/{token_address}'
    base_token_name, base_token_address, quote_token_name, quote_token_address,pair_address, market_cap, pool_id = processing_coin_info(token_url, network)
    trade_api = GET_TRADE_HISTORY.format(pool_id)
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
        "trending":'https://t.me/cointransactionchannel',
        "ads_text":'ETH TRENDING (LIVE)',
        "ads_url":'https://t.me/cointransactionchannel'
    }
    last_transaction = await database['transactions'].find_one({"pool_id": token_dict['pool_id']})
    logger.info('last trans %s' % last_transaction)
    async with aiohttp.ClientSession() as session:
        async with session.get(trade_api, headers=headers) as response:
            data = await response.json()
            list_trades = data['data']['transactions']
    if last_transaction is None:
        first_trade = list_trades[0]
        if first_trade['type'] == 'buy':
            await database["transactions"].insert_one({'pool_id':token_dict['pool_id'], 'last_transaction':json.dumps(first_trade)})
            from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(first_trade['txn'])['from']
            display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
            eth_value = round(usd_to_eth(float(first_trade['totalUsd'])),2)
            try:
                current_market_cap = read_socket(token_dict["network"], token_dict["pair_address"])['pair']['marketCap']
            except Exception as ex:
                current_market_cap = 0
            # telegram_bot.send_message(message_text=telegram_message_format.format(format_count(count), token['base_token_name'], token['token_telegram'], token['base_token_name'],token['token_telegram'], token['description'],eth_value, round(float(first_trade['totalUsd']),2),display_from_address ,from_address, first_trade['txn'], '{:,}'.format(current_market_cap), token['chart'], token['trade'], token['snipe'], token['trending']), button_text=token['ads_text'], button_url=token['ads_url'])
            return {
                'token':token_dict,
                'eth_value':eth_value,
                'display_from_address':display_from_address,
                'total_usd':round(float(first_trade['totalUsd']),2),
                'from_address':from_address,
                'txn':first_trade['txn'],
                'current_market_cap':'{:,}'.format(current_market_cap)
            }        
        else:
            logger.info('no new transaction')
            return 
    else:
        json_last_transaction = json.loads(last_transaction['last_transaction'])
        index_last_transaction = 0
        for trade in list_trades:
            if trade['time'] == json_last_transaction['time']:
                index_last_transaction = list_trades.index(trade)
        if index_last_transaction != 0:
            print('index', index_last_transaction)
            if index_last_transaction == 1:
                new_list_trades = list_trades[:index_last_transaction]
            else:
                new_list_trades = list_trades[:index_last_transaction-1]
            for new_trade in new_list_trades:
                if new_trade['type'] == 'buy':
                    last_transaction_update = await database["transactions"].update_one(
                        {"pool_id": token_dict['pool_id']},
                        {"$set": {'last_transaction':json.dumps(new_trade)}}
                    )
                    if last_transaction_update.modified_count == 1:
                        print('last transaction updated to db')
                    from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(new_trade['txn'])['from']
                    display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
                    eth_value = round(usd_to_eth(float(new_trade['totalUsd'])),2)
                    try:
                        current_market_cap = read_socket(token_dict["network"], token_dict["pair_address"])['pair']['marketCap']
                    except Exception as ex:
                        current_market_cap = 0
                    return {
                        'token':token_dict,
                        'eth_value':eth_value,
                        'display_from_address':display_from_address,
                        'total_usd':round(float(new_trade['totalUsd']),2),
                        'from_address':from_address,
                        'txn':new_trade['txn'],
                        'current_market_cap':'{:,}'.format(current_market_cap)
                    }       
                    # telegram_bot.send_message(message_text=telegram_message_format.format(format_count(count), token['base_token_name'], token['token_telegram'], token['base_token_name'], token['token_telegram'], token['description'],eth_value, round(float(new_trade['totalUsd']),2),display_from_address ,from_address, new_trade['txn'], '{:,}'.format(current_market_cap), token['chart'], token['trade'], token['snipe'], token['trending']), button_text=token['ads_text'], button_url=token['ads_url'])
        else:
            logger.info('no new transaction')
            return 
    
    
def send_token_info(context): 
    chat_id, network, token_address, description = context.job.context
    
    # Get the result of the async function using the 'result()' method
    result = asyncio.run(process_get_transaction_by_token(network, token_address,description))
    print("Result from async function:", result)
    

    context.bot.send_message(chat_id=chat_id, text=result.get('token'))
    
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
