import json
from pathlib import Path


class Database:
    def __init__(self, filename="waffle_chain.json"):
        self.filename = Path(filename)

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

    def load(self):
        if not self.filename.exists():
            return []

        return json.loads(
            self.filename.read_text(encoding="utf-8")
        )
