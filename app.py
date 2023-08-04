import uvicorn
import aiohttp
import json

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from database import database
from models import TokenModel, ResponseModel, token_helper, Network
from process import processing_coin_info
from loguru import logger
from token_socket import read_socket
from config import GET_TRADE_HISTORY, INFURA_ID
from transaction import EthereumTransaction
from utils import usd_to_eth

app = FastAPI()


@app.post("/add_token", response_description="Add new token")
async def add_token(token_url: str, description: str, token_telegram: str, chart: str, snipe: str, trade: str,
                    trending: str, ads_text: str, ads_url: str, network: Network = Network.ETH):
    base_token_name, base_token_address, quote_token_name, quote_token_address, pair_address, market_cap, pool_id = processing_coin_info(
        token_url, network.value)
    if base_token_address is None or pool_id is None:
        logger.info(base_token_address)
        logger.info(pool_id)
        return ResponseModel(data=None, message="Insert failed. Please try again")
    else:
        token_dict = {
            "base_token_name": base_token_name,
            "base_token_address": base_token_address,
            "quote_token_name": quote_token_name,
            "quote_token_address": quote_token_address,
            "pair_address": pair_address,
            "network": network.value,
            "market_cap": market_cap,
            "pool_id": pool_id,
            "description": description,
            "token_telegram": token_telegram,
            "chart": chart,
            "snipe": snipe,
            "trade": trade,
            "trending": trending,
            "ads_text": ads_text,
            "ads_url": ads_url
        }
        token = TokenModel(**token_dict)
        token = jsonable_encoder(token)
        token = await database["tokens"].insert_one(token)
        new_token = await database["tokens"].find_one({"_id": token.inserted_id})
        return ResponseModel(data=token_helper(new_token), message="Insert successfully")


@app.get("/get_tokens", response_description="Get list tokens")
async def get_tokens():
    list_tokens_db = await database['tokens'].find().to_list(50)
    tokens = [token_helper(token) for token in list_tokens_db]
    return ResponseModel(data=tokens, message="Get list tokens successfully")


@app.put('/update_token', response_description="Update token by pair address")
async def update_tokens(token_url: str, description: str = None, token_telegram: str = None, chart: str = None,
                        snipe: str = None, trade: str = None, trending: str = None, ads_text: str = None,
                        ads_url: str = None, network: Network = Network.ETH):
    try:
        update_field = {}
        socket_message = read_socket(network.value, token_url.split('/')[-1])
        pair_address = socket_message['pair']['pairAddress']
        if description is not None:
            update_field['description'] = description
        if token_telegram is not None:
            update_field['token_telegram'] = token_telegram
        if chart is not None:
            update_field['chart'] = chart
        if snipe is not None:
            update_field['snipe'] = snipe
        if trade is not None:
            update_field['trade'] = trade
        if trending is not None:
            update_field['trending'] = trending
        if ads_text is not None:
            update_field['ads_text'] = ads_text
        if ads_url is not None:
            update_field['ads_url'] = ads_url
        update_result = await database["tokens"].update_one({"pair_address": pair_address}, {"$set": update_field})
        if update_result.modified_count == 1:
            if await database["tokens"].find_one({"pair_address": pair_address}) is not None:
                return ResponseModel(data=update_field, message="Update token successfully")
    except Exception as ex:
        logger.info(str(ex))
        return ResponseModel(data=None, message="Update failed. Please try again")
    return ResponseModel(data=None, message="Update failed. Please try again")


@app.delete('/delete_token', response_description="Delete token by pair address")
async def delete_token(token_url: str, network: Network = Network.ETH):
    try:
        socket_message = read_socket(network.value, token_url.split('/')[-1])
        pair_address = socket_message['pair']['pairAddress']
        await database["tokens"].delete_one({"pair_address": pair_address})
        return ResponseModel(data=True, message="Delete token successfully")
    except Exception as ex:
        return ResponseModel(data=False, message="Delete token failed.Please try again")


@app.post('/get_last_transaction', response_description="Get last transaction by pool_id")
async def get_last_transaction(token: dict):
    try:
        last_transaction = await database['command_transactions'].find_one({"pool_id": token['pool_id']})

        trade_api = GET_TRADE_HISTORY.format(token['pool_id'])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(trade_api, headers=headers) as response:
                data = await response.json()
                list_trades = data['data']['transactions']
        if last_transaction is None:
            for trade in list_trades:
                if trade['type'] == 'buy':
                    await database["command_transactions"].insert_one(
                        {'pool_id': token['pool_id'], 'last_transaction': json.dumps(trade)})
                    from_address = EthereumTransaction(INFURA_ID).get_transaction_by_hash(trade['txn'])['from']
                    display_from_address = '{}...{}'.format(from_address[:6], from_address[-4:])
                    eth_value = round(usd_to_eth(float(trade['totalUsd'])), 2)
                    try:
                        current_market_cap = read_socket(token["network"], token["pair_address"])['pair']['marketCap']
                    except Exception as ex:
                        current_market_cap = 0
                    return {'data': [{
                        'token': token,
                        'total_usd': round(float(trade['totalUsd']), 2),
                        'display_from_address': display_from_address,
                        'from_address': from_address,
                        'txn': trade['txn'],
                        'eth_value': eth_value,
                        'current_market_cap': '{:,}'.format(current_market_cap)
                    }]}
        else:
            json_last_transaction = json.loads(last_transaction['last_transaction'])
            logger.info('LAST TRANSACTION %s' % json_last_transaction)
            count = 0
            for trade in list_trades:
                count += 1
                if int(trade['time']) > int(json_last_transaction['time']) and trade['type'] == 'buy':
                    last_transaction_update = await database["command_transactions"].update_one(
                        {"pool_id": token['pool_id']},
                        {"$set": {'last_transaction': json.dumps(trade)}}
                    )
                    if last_transaction_update.modified_count == 1:
                        logger.info('last transaction updated to db')
                    logger.info('NEW BUY TRANSACTION %s' % trade)
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
                if count == len(list_trades):
                    logger.info('NO NEW TRANSACTION')
                    return {'data': None}
    except Exception as ex:
        logger.info('GET LAST TRANSACTION ERROR %s' % str(ex))
        return {'data': None}


if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8888)
