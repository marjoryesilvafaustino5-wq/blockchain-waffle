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
                chain_data = data.get("chain", [])

                if not chain_data:
                    continue

                candidate_chain = []

                for block_data in chain_data:
                    block = Block(
                        index=block_data["index"],
                        timestamp=block_data["timestamp"],
                        data=block_data["data"],
                        previous_hash=block_data["previous_hash"],
                        nonce=block_data["nonce"],
                    )

                    received_hash = block_data.get("hash", "")
                    block.stored_hash = received_hash

                    candidate_chain.append(block)

                if not self._is_valid_chain(candidate_chain):
                    continue

                if (
                    longest_chain is None
                    or len(candidate_chain) > len(longest_chain)
                ):
                    longest_chain = candidate_chain

            except (requests.RequestException, KeyError, TypeError, ValueError):
                continue

        if longest_chain and len(longest_chain) > len(blockchain.chain):
            blockchain.chain = longest_chain

            if blockchain.database:
                blockchain.database.save(blockchain)

            return blockchain.chain

        return None

    def _is_valid_chain(self, chain, difficulty=4):
        if not chain:
            return False

        target = "0" * difficulty

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

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

        return True
