import requests
import asyncio
from token_socket import WebSocketClient
from database import database
from loguru import logger

async def update_token_market_cap(token):
    socket_url = f'wss://io.dexscreener.com/dex/screener/pair/{token["network"]}/{token["pair_address"]}'
    websocket_client = WebSocketClient(socket_url)
    websocket_client.run_forever(origin="https://dexscreener.com")
    token_info_message = websocket_client.get_message()
    market_cap = token_info_message['pair']['marketCap']
    update_market_cap = {
        'market_cap': market_cap
    }
    update_result = await database["tokens"].update_one(
        {"pair_address": token['pair_address']},
        {"$set": update_market_cap}
    )
    if update_result.modified_count == 1:
        logger.info('Token %s updated market cap %s' % (token['pair_address'], market_cap))

async def main():
    while True:
        try:
            list_tokens = requests.get('http://localhost:8888/get_tokens').json()['data']
            tasks = [update_token_market_cap(token) for token in list_tokens]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error updating token market cap: {e}")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
