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
        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.previous_hash != previous.hash():
                return False

        return True
