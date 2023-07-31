import requests
import json
import asyncio
import aiohttp

from config import GET_TRADE_HISTORY,CHAT_ID, BOT_TOKEN, INFURA_ID, CONVERT_USD_ETH
from transaction import EthereumTransaction
from database import database
from telegram_handler import TelegramBot
from token_socket import read_socket

telegram_bot = TelegramBot(BOT_TOKEN, CHAT_ID)
telegram_bot.run()

telegram_message_format = """
{} | [{}]({}) \n 
[{}]({}) BUY! \n 
{} \n 
💵 {} ETH (${}) \n 
🔹 [{}](https://etherscan.io/address/{}) | [Txn](https://etherscan.io/tx/{}) \n 
✅ *New Holder* \n 
🔼 Market Cap $*{}* \n 
🦎 [Chart]({})   ✨[Trade]({}) \n 
🦄 [Snipe]({})   🔹[Trending]({}) 
"""
def format_count(count):
    if count == 1:
        return "1️⃣"
    elif count == 2:
        return "2️⃣"
    elif count == 3:
        return "3️⃣"
    elif count == 4:
        return "4️⃣"
    elif count == 5:
        return "5️⃣"
    elif count == 6:
        return "6️⃣"
    elif count == 7:
        return "7️⃣"
    elif count == 8:
        return "8️⃣"
    else:
        return '9️⃣'

def get_eth_price_in_usd():
    params = {'ids': 'ethereum', 'vs_currencies': 'usd'}
    try:
        response = requests.get(CONVERT_USD_ETH, params=params)
        data = response.json()

        if 'ethereum' in data and 'usd' in data['ethereum']:
            return data['ethereum']['usd']
        else:
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    
def usd_to_eth(usd_value):
    eth_price = get_eth_price_in_usd()

    if eth_price is not None:
        eth_value = usd_value / eth_price
        return eth_value
    else:
        return None

async def process_token_trade_history(token, count):
    trade_api = GET_TRADE_HISTORY.format(token['pool_id'])
    print('pool_id', token['pool_id'])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
    }
    # select last transaction from db
    last_transaction = await database['transactions'].find_one({"pool_id": token['pool_id']})
    async with aiohttp.ClientSession() as session:
        async with session.get(trade_api, headers=headers) as response:
            data = await response.json()
            list_trades = data['data']['transactions']
    if last_transaction is None:
        first_trade = list_trades[0]
        if first_trade['type'] == 'buy':
            await database["transactions"].insert_one({'pool_id':token['pool_id'], 'last_transaction':json.dumps(first_trade)})
            from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(first_trade['txn'])['from']
            display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
            eth_value = round(usd_to_eth(float(first_trade['totalUsd'])),2)
            try:
                current_market_cap = read_socket(token["network"], token["pair_address"])['pair']['marketCap']
            except Exception as ex:
                current_market_cap = 0
            telegram_bot.send_message(message_text=telegram_message_format.format(format_count(count), token['base_token_name'], token['token_telegram'], token['base_token_name'],token['token_telegram'], token['description'],eth_value, round(float(first_trade['totalUsd']),2),display_from_address ,from_address, first_trade['txn'], '{:,}'.format(current_market_cap), token['chart'], token['trade'], token['snipe'], token['trending']), button_text=token['ads_text'], button_url=token['ads_url'])
        else:
            print('no new transaction')
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
                        {"pool_id": token['pool_id']},
                        {"$set": {'last_transaction':json.dumps(new_trade)}}
                    )
                    if last_transaction_update.modified_count == 1:
                        print('last transaction updated to db')
                    from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(new_trade['txn'])['from']
                    display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
                    eth_value = round(usd_to_eth(float(new_trade['totalUsd'])),2)
                    try:
                        current_market_cap = read_socket(token["network"], token["pair_address"])['pair']['marketCap']
                    except Exception as ex:
                        current_market_cap = 0
                    telegram_bot.send_message(message_text=telegram_message_format.format(format_count(count), token['base_token_name'], token['token_telegram'], token['base_token_name'], token['token_telegram'], token['description'],eth_value, round(float(new_trade['totalUsd']),2),display_from_address ,from_address, new_trade['txn'], '{:,}'.format(current_market_cap), token['chart'], token['trade'], token['snipe'], token['trending']), button_text=token['ads_text'], button_url=token['ads_url'])
        else:
            print('no new transaction')

async def main():
    while True:
        try:
            list_tokens = requests.get('http://localhost:8888/get_tokens').json()['data']
            sorted_list_tokens = sorted(list_tokens, key=lambda d: d['market_cap'], reverse=True)
            # Create a list of tasks, one for each token
            tasks = [process_token_trade_history(token, count+1) for count, token in enumerate(sorted_list_tokens)]

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error fetching token data: {e}")
        await asyncio.sleep(5)
        
if __name__ == "__main__":
    asyncio.run(main())
            

