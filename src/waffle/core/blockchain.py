from .block import Block
from src.waffle.storage.database import Database

WFL_SYMBOL = "WFL"
BLOCK_REWARD = 50.0
MAX_SUPPLY = 21_000_000.0
FEE_ADDRESS = "WAFFLE_FEES"
ADMIN_ADDRESS = "WAFFLE_ADMIN"


class Blockchain:
    def __init__(self, database=None):
        self.database = database

        if self.database:
            saved_blocks = self.database.load()
        else:
            saved_blocks = []

        if saved_blocks:
            self.chain = [
                Block(
                    index=block["index"],
                    timestamp=block["timestamp"],
                    data=block["data"],
                    previous_hash=block["previous_hash"],
                    nonce=block["nonce"],
                )
                for block in saved_blocks
            ]
        else:
            self.chain = [self.create_genesis_block()]

        self.pending_transactions = self._load_pending_transactions()

    def _load_pending_transactions(self):
        if not self.database:
            return []

        from .transaction import Transaction

        transactions = []

        for item in self.database.load_pending():
            transaction = Transaction(
                sender=item["sender"],
                recipient=item["recipient"],
                amount=item["amount"],
                signature=item.get("signature", ""),
            )
            transactions.append(transaction)

        return transactions

    def create_genesis_block(self):
        return Block(
            index=0,
            timestamp=0,
            data={"message": "Genesis Block"},
            previous_hash="0",
        )

    def add_transaction(self, transaction, wallet):
        if transaction.amount <= 0:
            raise ValueError("Invalid transaction amount")
        if not transaction.is_valid(wallet):
            raise ValueError("Invalid transaction signature")
        confirmed_balance = self.get_balance(transaction.sender)
        pending_total = sum(
            pending.total
            for pending in self.pending_transactions
            if pending.sender == transaction.sender
        )

        if confirmed_balance - pending_total < transaction.total:
            raise ValueError("Insufficient balance")

        self.pending_transactions.append(transaction)

        if self.database:
            self.database.save_pending(self.pending_transactions)

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

        if self.database:
            self.database.save(self)

        return block

    def mine_pending_transactions(self, difficulty=4, miner_address=None):
        transactions = [
            {
                "sender": t.sender,
                "recipient": t.recipient,
                "amount": t.amount,
                "fee": t.fee,
                "signature": t.signature,
            }
            for t in self.pending_transactions
        ]

        if miner_address:
            current_supply = sum(
                transaction["amount"]
                for block in self.chain
                for transaction in block.data.get("transactions", [])
                if transaction.get("sender") == "SYSTEM"
            )
            reward = min(BLOCK_REWARD, MAX_SUPPLY - current_supply)
            if reward > 0:
                transactions.append({
                    "sender": "SYSTEM",
                    "recipient": miner_address,
                    "amount": reward,
                    "signature": "",
                })

        fee_total = sum(transaction.get("fee", 0.0) for transaction in transactions)

        if fee_total > 0:
            transactions.append({
                "sender": "SYSTEM",
                "recipient": FEE_ADDRESS,
                "amount": fee_total,
                "signature": "",
            })

        data = {"transactions": transactions}
        block = self.add_block(data)
        self.mine_block(block, difficulty)
        self.pending_transactions = []

        if self.database:
            self.database.save_pending(self.pending_transactions)

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

    def get_fee_balance(self):
        return self.get_balance(FEE_ADDRESS)

    def withdraw_fees(self, admin_address, recipient):
        if admin_address != ADMIN_ADDRESS:
            raise ValueError("Unauthorized fee withdrawal")

        amount = self.get_fee_balance()

        if amount <= 0:
            raise ValueError("No fees available")

        transaction = {
            "sender": FEE_ADDRESS,
            "recipient": recipient,
            "amount": amount,
            "fee": 0.0,
            "signature": "",
        }

        block = self.add_block({
            "transactions": [transaction],
        })

        self.mine_block(block)

        return transaction

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

            transactions = current.data.get("transactions", [])
            for transaction in transactions:
                if transaction.get("sender") == "SYSTEM":
                    if transaction.get("signature") != "":
                        return False

                    if transaction.get("recipient") == FEE_ADDRESS:
                        if transaction.get("amount", 0) <= 0:
                            return False
                    elif transaction.get("amount") != BLOCK_REWARD:
                        return False

        return True
