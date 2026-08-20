import hashlib
import json
from dataclasses import dataclass


@dataclass
class Block:
    index: int
    timestamp: float
    data: dict
    previous_hash: str
    nonce: int = 0

    def hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }

        encoded = json.dumps(
            block_data,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

        return hashlib.sha256(encoded).hexdigest()
