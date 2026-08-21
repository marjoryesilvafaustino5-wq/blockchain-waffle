import hashlib
import json
import secrets
from pathlib import Path


class Wallet:
    def __init__(self, private_key=None):
        self.private_key = private_key or secrets.token_hex(32)
        self.address = self._create_address()

    def _create_address(self):
        return hashlib.sha256(
            self.private_key.encode()
        ).hexdigest()[:40]

    def sign(self, message):
        data = f"{self.private_key}:{message}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify(self, message, signature):
        return self.sign(message) == signature


WALLETS_FILE = Path("waffle_wallets.json")


def load_wallets():
    wallets = {}

    if WALLETS_FILE.exists():
        data = json.loads(
            WALLETS_FILE.read_text(encoding="utf-8")
        )

        for item in data:
            wallet = Wallet(private_key=item["private_key"])
            wallets[wallet.address] = wallet

    return wallets


def save_wallet(wallets):
    WALLETS_FILE.write_text(
        json.dumps(
            [
                {
                    "address": wallet.address,
                    "private_key": wallet.private_key,
                }
                for wallet in wallets.values()
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
