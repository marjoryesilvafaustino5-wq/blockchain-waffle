from .block import Block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(
            index=0,
            timestamp=0,
            data={"message": "Genesis Block"},
            previous_hash="0",
        )

    def add_transaction(self, transaction, wallet):
        if not transaction.is_valid(wallet):
            raise ValueError("Invalid transaction signature")
        if self.get_balance(transaction.sender) < transaction.amount:
            raise ValueError("Insufficient balance")
        self.pending_transactions.append(transaction)

    def add_block(self, data):
        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=__import__("time").time(),
            data=data,
            previous_hash=previous_block.hash(),
        )

        self.chain.append(new_block)
        return new_block

    def mine_block(self, block, difficulty=4):
        target = "0" * difficulty
        while not block.hash().startswith(target):
            block.nonce += 1
        block.stored_hash = block.hash()
        return block

    def mine_pending_transactions(self, difficulty=4, miner_address=None):
        if not self.pending_transactions:
            return None

        transactions = [t.__dict__ for t in self.pending_transactions]

        if miner_address:
            transactions.append({
                "sender": "SYSTEM",
                "recipient": miner_address,
                "amount": 50.0,
                "signature": "",
            })

        data = {"transactions": transactions}
        block = self.add_block(data)
        self.mine_block(block, difficulty)
        self.pending_transactions = []
        return block

    def get_balance(self, address):
        balance = 0.0

        for block in self.chain[1:]:
            transactions = block.data.get("transactions", [])
            for transaction in transactions:
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
                if transaction["recipient"] == address:
                    balance += transaction["amount"]

        return balance

    def is_valid(self, difficulty=4):
        target = "0" * difficulty

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash() != current.stored_hash:
                return False
            if not current.hash().startswith(target):
                return False
            if current.previous_hash != previous.hash():
                return False

        return True
