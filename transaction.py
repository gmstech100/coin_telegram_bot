from web3 import Web3
from config import INFURA_ID

class EthereumTransaction:
    def __init__(self, infura_project_id):
        # Set up the Infura URL using the provided Project ID
        self.infura_project_id = infura_project_id
        self.eth_node_url = f'https://mainnet.infura.io/v3/{infura_project_id}'

        # Connect to the Ethereum node
        self.w3 = Web3(Web3.HTTPProvider(self.eth_node_url))

    def get_transaction_by_hash(self, tx_hash):
        try:
            # Get the transaction details
            transaction = self.w3.eth.get_transaction(tx_hash)

            if transaction:
                return transaction
            else:
                return None
        except Exception as e:
            print('Error:', e)
            return None