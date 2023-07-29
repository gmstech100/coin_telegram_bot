from database import database
from loguru import logger
from token_socket import WebSocketClient


def processing_coin_info(url, network):
    try:
        socket_url = 'wss://io.dexscreener.com/dex/screener/pair/{}/{}'.format(network, url.split('/')[-1])
        logger.info(socket_url)
        websocket_client = WebSocketClient(socket_url)
        websocket_client.run_forever(origin="https://dexscreener.com")
        token_info_message = websocket_client.get_message()
        base_token_name = token_info_message['pair']['baseToken']['name']
        base_token_address = token_info_message['pair']['baseToken']['address']
        quote_token_name = token_info_message['pair']['quoteToken']['name']
        quote_token_address = token_info_message['pair']['quoteToken']['address']
        market_cap = token_info_message['pair']['marketCap']
        return base_token_name, base_token_address, quote_token_name, quote_token_address, market_cap
    except Exception as ex:
        logger.info(f'PROCESSING COIN INFO ERROR :{str(ex)}')
        return None, None, None, None, None
    
async def insert_token(token):
    new_token = await database["tokens"].insert_one(token)
    return new_token

async def get_tokens():
    return database['tokens'].find()


    

