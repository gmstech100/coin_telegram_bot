from database import database
from loguru import logger
from token_socket import read_socket
from models import NETWORK_PLATFORM_ID
from config import GET_TOKEN_INFO, GET_TRADE_HISTORY, INFURA_ID
from transaction import EthereumTransaction
from utils import usd_to_eth

import requests
import aiohttp
import json


def get_pool_id(base_token_address, network, pair_address):
    try:
        platform_id = NETWORK_PLATFORM_ID.get(network)
        params = {
            'base-address': base_token_address,
            'start': 1,
            'limit': 10,
            'platform-id': platform_id
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


async def processing_coin_transaction(token):
    trade_api = GET_TRADE_HISTORY.format(token['pool_id'])
    logger.info('pool_id %s' % token['pool_id'])
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
        for trade in list_trades:
            if trade['type'] == 'buy':
                await database["transactions"].insert_one(
                    {'pool_id': token['pool_id'], 'last_transaction': json.dumps(trade)})
                from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(trade['txn'])['from']
                display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
                eth_value = round(usd_to_eth(float(trade['totalUsd'])), 2)
                try:
                    current_market_cap = read_socket(token["network"], token["pair_address"])['pair']['marketCap']
                except Exception as ex:
                    current_market_cap = 0
                return {'data': {
                    'token': token,
                    'total_usd': round(float(trade['totalUsd']), 2),
                    'display_from_address': display_from_address,
                    'from_address': from_address,
                    'txn': trade['txn'],
                    'eth_value': eth_value,
                    'current_market_cap': '{:,}'.format(current_market_cap)
                }}
            else:
                logger.info('NO NEW TRANSACTION')
                return {'data': None}
    else:
        json_last_transaction = json.loads(last_transaction['last_transaction'])
        for trade in list_trades:
            if int(trade['time']) > int(json_last_transaction['time']) and trade['type'] == 'buy':

                last_transaction_update = await database["transactions"].update_one(
                    {"pool_id": token['pool_id']},
                    {"$set": {'last_transaction': json.dumps(trade)}}
                )
                if last_transaction_update.modified_count == 1:
                    print('last transaction updated to db')
                from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(trade['txn'])['from']
                display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
                eth_value = round(usd_to_eth(float(trade['totalUsd'])), 2)
                try:
                    current_market_cap = read_socket(token["network"], token["pair_address"])['pair']['marketCap']
                except Exception as ex:
                    current_market_cap = 0
                trade_dict = {
                    'token': token,
                    'total_usd': round(float(trade['totalUsd']), 2),
                    'display_from_address': display_from_address,
                    'from_address': from_address,
                    'txn': trade['txn'],
                    'eth_value': eth_value,
                    'current_market_cap': '{:,}'.format(current_market_cap)
                }
                return {'data': trade_dict}
        else:
            logger.info('NO NEW TRANSACTION')
            return {'data': None}
