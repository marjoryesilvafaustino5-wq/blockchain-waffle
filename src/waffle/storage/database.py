import json
from pathlib import Path


class Database:
    def __init__(self, filename="waffle_chain.json"):
        self.filename = Path(filename)
        self.pending_filename = self.filename.with_name(
            "waffle_pending.json"
        )

    def save(self, blockchain):
        data = []

        for block in blockchain.chain:
            data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
            })

        self.filename.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

        self.save_pending(blockchain.pending_transactions)

    def load(self):
        if not self.filename.exists():
            return []

        return json.loads(
            self.filename.read_text(encoding="utf-8")
        )

    def save_pending(self, transactions):
        data = []

        for transaction in transactions:
            data.append({
                "sender": transaction.sender,
                "recipient": transaction.recipient,
                "amount": transaction.amount,
                "fee": transaction.fee,
                "signature": transaction.signature,
            })

        self.pending_filename.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def load_pending(self):
        if not self.pending_filename.exists():
            return []

        return json.loads(
            self.pending_filename.read_text(encoding="utf-8")
        )
