import json
from pathlib import Path

from src.waffle.core.block import Block


class NodeNetwork:
    def __init__(self, filename="waffle_nodes.json"):
        self.filename = Path(filename)
        self.nodes = set()
        self._load()

    def _load(self):
        if self.filename.exists():
            self.nodes = set(
                json.loads(
                    self.filename.read_text(encoding="utf-8")
                )
            )

    def _save(self):
        self.filename.write_text(
            json.dumps(
                sorted(self.nodes),
                indent=2,
            ),
            encoding="utf-8",
        )

    def add_node(self, address):
        self.nodes.add(address)
        self._save()

    def remove_node(self, address):
        self.nodes.discard(address)
        self._save()

    def get_nodes(self):
        return sorted(self.nodes)

    def replace_chain(self, blockchain):
        import requests

        longest_chain = None

        for address in self.nodes:
            try:
                response = requests.get(
                    f"{address}/network/chain",
                    timeout=3,
                )

                if response.status_code != 200:
                    continue

                data = response.json()
                chain = data.get("chain", [])

                if longest_chain is None or len(chain) > len(longest_chain):
                    longest_chain = chain

            except requests.RequestException:
                continue

        if longest_chain and len(longest_chain) > len(blockchain.chain):
            blockchain.chain = [
                Block(
                    index=block["index"],
                    timestamp=block["timestamp"],
                    data=block["data"],
                    previous_hash=block["previous_hash"],
                    nonce=block["nonce"],
                    stored_hash=block.get("hash", ""),
                )
                for block in longest_chain
            ]
            return blockchain.chain

        return None
