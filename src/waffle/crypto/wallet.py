import hashlib
import json
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)


class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = secrets.token_hex(32)

        self._private_key_bytes = bytes.fromhex(self.private_key)
        self._signing_key = Ed25519PrivateKey.from_private_bytes(
            self._private_key_bytes
        )
        self._public_key = self._signing_key.public_key()

        self.address = self._create_address()

    def _create_address(self):
        return hashlib.sha256(
            self.private_key.encode()
        ).hexdigest()[:40]

    def sign(self, message):
        if not isinstance(message, str):
            message = str(message)

        signature = self._signing_key.sign(message.encode("utf-8"))
        return signature.hex()

    def verify(self, message, signature):
        try:
            if not isinstance(message, str):
                message = str(message)

            self._public_key.verify(
                bytes.fromhex(signature),
                message.encode("utf-8"),
            )
            return True
        except (ValueError, TypeError):
            return False

    def public_key(self):
        return self._public_key.public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        ).hex()


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
                    "public_key": wallet.public_key(),
                }
                for wallet in wallets.values()
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
