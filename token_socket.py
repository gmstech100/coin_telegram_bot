import websocket
import json

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183',
            'Sec-Websocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        self.received_message = None
        self.ws = None

    def on_message(self, ws, message):
        self.received_message = json.loads(message)
        ws.close()  # Close the WebSocket connection after receiving the message

    def get_message(self):
        return self.received_message

    def run_forever(self, origin=None):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            header=self.header
        )
        self.ws.run_forever(origin=origin)