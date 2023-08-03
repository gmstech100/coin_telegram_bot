import requests
from config import CONVERT_USD_ETH

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