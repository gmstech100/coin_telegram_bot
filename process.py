from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from config import GET_TOKEN_INFO, GET_TRADE_HISTORY
from database import database
from loguru import logger
from models import NETWORK_PLATFORM_ID

import requests
import time

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

def processing_coin_info(url, network):
    try:
        page = Request(url=url,headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(urlopen(page).read(),'html.parser')
        base_token_address = soup.find('div',{'class':'frteJV'}).find('a')['href'].split('/')[-1]
        logger.info(base_token_address)
        base_token_pool_id = get_coin_info(base_token_address, network)['data'][0]['poolId']
        logger.info(base_token_pool_id)
        return base_token_address, base_token_pool_id
    except Exception as ex:
        logger.info(f'PROCESSING COIN INFO ERROR :{str(ex)}')
        return None, None
    


async def insert_token(token):
    new_token = await database["tokens"].insert_one(token)
    return new_token

async def get_tokens():
    return database['tokens'].find()

