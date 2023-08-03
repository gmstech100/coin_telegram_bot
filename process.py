from database import database
from loguru import logger
from token_socket import read_socket
from models import NETWORK_PLATFORM_ID
from config import GET_TOKEN_INFO

import requests

def get_pool_id(base_token_address, network, pair_address):
    try:
        platform_id = NETWORK_PLATFORM_ID.get(network)
        params = {
            'base-address':base_token_address,
            'start':1,
            'limit':10,
            'platform-id':platform_id
        }
        res_data = requests.get(GET_TOKEN_INFO, params=params).json()['data']
        for data in res_data:
            logger.info(data)
            if data['pairContractAddress'].lower() == pair_address.lower():
                return data['poolId']
    except Exception as ex:
        logger.info(f'PROCESSING COIN POOL ID :{str(ex)}')
        return None

def processing_coin_info(url, network):
    try:
        token_info_message = read_socket(network, url.split('/')[-1])
        base_token_name = token_info_message['pair']['baseToken']['name']
        base_token_address = token_info_message['pair']['baseToken']['address']
        logger.info('BASE TOKEN ADDRESS: %s' % base_token_address)
        quote_token_name = token_info_message['pair']['quoteToken']['name']
        quote_token_address = token_info_message['pair']['quoteToken']['address']
        pair_address = token_info_message['pair']['pairAddress']
        logger.info('PAIR ADDRESS: %s' % pair_address)
        try:
            market_cap = token_info_message['pair']['marketCap']
        except Exception as ex:
            logger.info(f'MARKET CAP ERROR: {str(ex)}')
            market_cap = 0
        pool_id = get_pool_id(base_token_address, network, pair_address)
        return base_token_name, base_token_address, quote_token_name, quote_token_address, pair_address, market_cap, pool_id
    except Exception as ex:
        logger.info(f'PROCESSING COIN INFO ERROR :{str(ex)}')
        return None, None, None, None, None, None, None
    
async def insert_token(token):
    new_token = await database["tokens"].insert_one(token)
    return new_token

async def get_tokens():
    return database['tokens'].find()


    

