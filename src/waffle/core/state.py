class BlockchainState:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def get_balance(self, address):
        return self.blockchain.get_balance(address)

    def get_fee_balance(self):
        return self.blockchain.get_fee_balance()

    def get_circulating_supply(self):
        return sum(
            transaction["amount"]
            for block in self.blockchain.chain
            for transaction in block.data.get("transactions", [])
            if transaction.get("sender") == "SYSTEM"
        )
