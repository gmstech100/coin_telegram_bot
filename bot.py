import requests
import asyncio

from config import CHAT_ID, BOT_TOKEN, CONVERT_USD_ETH, LIST_TOKENS_LABELS
from telegram_handler import TelegramBot
from process import processing_coin_transaction

telegram_bot = TelegramBot(BOT_TOKEN, CHAT_ID)
telegram_bot.run()

transaction_count = 0

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


async def send_token_list_to_telegram(tokens):
    # Construct the message text
    telegram_message = """{}\n""".format(LIST_TOKENS_LABELS)
    for count, token in enumerate(tokens):
        telegram_message += '*{}* [{}]({})\n'.format(str(count + 1), token['base_token_name'], token['token_telegram'])
    # Send the message
    telegram_bot.send_message(message_text=telegram_message, button_text='ETH TRENDING LIVE',
                              button_url='https://t.me/cointransactionchannel')


async def process_token_trade_history(token, count):
    global transaction_count
    data = await processing_coin_transaction(token)
    if data['data'] is not None:
        transaction_data = data['data']
        telegram_bot.send_message(
            message_text=telegram_message_format.format(format_count(count), token['base_token_name'],
                                                        token['token_telegram'], token['base_token_name'],
                                                        token['token_telegram'], token['description'],
                                                        transaction_data['eth_value'],
                                                        transaction_data['total_usd'],
                                                        transaction_data['display_from_address'], transaction_data['from_address'], transaction_data['txn'],
                                                        transaction_data['current_market_cap'], token['chart'],
                                                        token['trade'], token['snipe'], token['trending']),
            button_text=token['ads_text'], button_url=token['ads_url'])
        transaction_count += 1

    # Increment the transaction count
    if transaction_count % 100 == 0:
        # Fetch the list of tokens from the local server
        list_tokens = requests.get('http://localhost:8888/get_tokens').json()['data']
        sorted_list_tokens = sorted(list_tokens, key=lambda d: d['market_cap'], reverse=True)

        # Send the list of tokens to Telegram
        await send_token_list_to_telegram(sorted_list_tokens)
        transaction_count = 0


async def main():
    while True:
        try:
            list_tokens = requests.get('http://localhost:8888/get_tokens').json()['data']
            sorted_list_tokens = sorted(list_tokens, key=lambda d: d['market_cap'], reverse=True)
            # Create a list of tasks, one for each token
            tasks = [process_token_trade_history(token, count + 1) for count, token in enumerate(sorted_list_tokens)]

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error fetching token data: {e}")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
