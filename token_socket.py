import websocket
import json
from loguru import logger

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183',
            # 'Sec-Websocket-Extensions': 'permessage-deflate; client_max_window_bits',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'en-US,en;q=0.9',
            # 'Cache-Control': 'no-cache'
        }
        self.received_message = None
        self.ws = None

    def on_message(self, ws, message):
        self.received_message = json.loads(message)
        ws.close()  # Close the WebSocket connection after receiving the message

    def get_message(self):
        return self.received_message
    
    def get_pair_address(self):
        return self.received_message['pair']['pairAddress']
    
    def get_market_cap(self):
        return self.received_message['pair']['marketCap']

    def run_forever(self, origin=None):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            header=self.header
        )
        self.ws.run_forever(origin=origin)
        
        
def read_socket(network,pair_address):
    socket_url = 'wss://io.dexscreener.com/dex/screener/pair/{}/{}'.format(network, pair_address)
    logger.info(socket_url)
    websocket_client = WebSocketClient(socket_url)
    websocket_client.run_forever(origin="https://dexscreener.com")
    return websocket_client.get_message()
