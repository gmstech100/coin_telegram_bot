from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from config import GET_TOKEN_INFO, GET_TRADE_HISTORY, GET_BASE_TOKEN
from database import database
from loguru import logger
from models import NETWORK_PLATFORM_ID
from token_socket import WebSocketClient

import requests
import time
import re

def get_coin_info(base_token_address, network):
    params = {
        'base-address': base_token_address,
        'start':1,
        'limit':10,
        'platform-id':NETWORK_PLATFORM_ID.get(network, 1)
    }
    return requests.get(GET_TOKEN_INFO, params=params).json()

def get_token_transaction(pool_id):
    api_url = GET_TRADE_HISTORY.format(pool_id)
    params = {
        'reverse-order':False
    }
    return requests.get(api_url, params=params).json()

def get_base_token_address(url):
    params = {
        'q':url.split('/')[-1]
    }
    print(params)
    return requests.get(GET_BASE_TOKEN, params=params).json()

def processing_coin_info(url, network):
    try:
        socket_url = 'wss://io.dexscreener.com/dex/screener/pair/{}/{}'.format(network, url.split('/')[-1])
        websocket_client = WebSocketClient(socket_url)
        websocket_client.run_forever(origin="https://dexscreener.com")
        token_info_message = websocket_client.get_message()
        base_token_address = token_info_message['pair']['baseToken']['address']
        market_cap = token_info_message['pair']['marketCap']
        base_token_name = token_info_message['pair']['baseToken']['name']
        base_token_pool_id = get_coin_info(base_token_address, network)['data'][0]['poolId']
        return base_token_name, base_token_address, base_token_pool_id, market_cap
    except Exception as ex:
        logger.info(f'PROCESSING COIN INFO ERROR :{str(ex)}')
        return None, None
    


async def insert_token(token):
    new_token = await database["tokens"].insert_one(token)
    return new_token

async def get_tokens():
    return database['tokens'].find()


    

