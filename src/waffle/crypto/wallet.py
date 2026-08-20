import hashlib
import secrets


class Wallet:
    def __init__(self):
        self.private_key = secrets.token_hex(32)
        self.address = self._create_address()

    def _create_address(self):
        return hashlib.sha256(
            self.private_key.encode()
        ).hexdigest()[:40]

    def sign(self, message):
        data = f"{self.private_key}:{message}"
        return hashlib.sha256(data.encode()).hexdigest()
