class BlockchainState:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def get_balance(self, address):
        return self.blockchain.get_balance(address)

    def get_fee_balance(self):
        return self.blockchain.get_fee_balance()
