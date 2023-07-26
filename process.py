from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from apis import GET_TOKEN_INFO, GET_TRADE_HISTORY

import requests
import time

def get_coin_info(base_token_address):
    params = {
        'base-address': base_token_address,
        'start':1,
        'limit':10,
        'platform-id':1
    }
    return requests.get(GET_TOKEN_INFO, params=params).json()

def get_token_transaction(pool_id):
    api_url = GET_TRADE_HISTORY.format(pool_id)
    params = {
        'reverse-order':False
    }
    return requests.get(api_url, params=params).json()

def processing_coin_info(url):
# url = 'https://coinmarketcap.com/dexscan/ethereum/0x7235c4aa48b753e48c3786ec60d3bddef5f4b27a/'
    page = Request(url=url,headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(urlopen(page).read(),'html.parser')
    base_token_address = soup.find('div',{'class':'frteJV'}).find('a')['href'].split('/')[-1]
    base_token_pool_id = get_coin_info(base_token_address)['data'][0]['poolId']
    return base_token_address, base_token_pool_id