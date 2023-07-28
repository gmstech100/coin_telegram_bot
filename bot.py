import requests
import json
import time
from config import CHAT_ID, BOT_TOKEN
from process import get_token_transaction

def send_telegram_message(message: str):
    data_dict = {'chat_id': CHAT_ID,
                 'text': message,
                 'parse_mode': 'HTML',
                 'disable_notification': True}
    headers = {'Content-Type': 'application/json',
               'Proxy-Authorization': 'Basic base64'}
    data = json.dumps(data_dict)
    params = {
        'parse_mode': 'Markdown'
    }
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    response = requests.post(url,
                             data=data,
                             headers=headers,
                             params=params,
                             verify=False)
    return response

if __name__ == "__main__":
    list_transactions = []
    while True:
        if len(list_transactions) == 0:
            first_transaction = get_token_transaction(7461333)['data']['transactions'][0]
            if first_transaction.get('type') == 'buy':
                list_transactions.append(first_transaction)
                send_telegram_message(str(first_transaction))
            else:
                print('no new transaction')
        else:
            first_transaction = list_transactions[0]
            list_current_transactions = get_token_transaction(7461333)['data']['transactions']
            index_first_transaction_in_list = list_current_transactions.index(next(item for item in list_current_transactions if item['time'] == first_transaction['time']))
            if index_first_transaction_in_list != 0:
                list_transactions = [item for item in list_current_transactions[:index_first_transaction_in_list] if item['type'] == 'buy']
                print('new transaction count: ', len(list_transactions))
                send_telegram_message(str(list_transactions))
            else:
                print('no new transaction')
        time.sleep(5)


