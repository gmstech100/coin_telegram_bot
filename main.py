from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests

def get_coin_info(base_token_address):
    api_url = 'https://api.coinmarketcap.com/dexer/v3/dexer/pair-list?'
    params = {
        'base-address': base_token_address,
        'start':1,
        'limit':10,
        'platform-id':1
    }
    return requests.get(api_url, params=params).json()

url = 'https://coinmarketcap.com/dexscan/ethereum/0x7235c4aa48b753e48c3786ec60d3bddef5f4b27a/'
page = Request(url=url,headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(urlopen(page).read(),'html.parser')
base_token_address = soup.find('div',{'class':'sc-3514e8c3-0'}).find('a')['href'].split('/')[-1]
print(base_token_address)
base_token_pool_id = get_coin_info(base_token_address)['data'][0]['poolId']
print(base_token_pool_id)