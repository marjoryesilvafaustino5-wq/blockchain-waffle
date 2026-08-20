from dataclasses import dataclass


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    signature: str = ""

    def message(self) -> str:
        return f"{self.sender}:{self.recipient}:{self.amount}"
    def is_valid(self, wallet) -> bool:
        return wallet.verify(self.message(), self.signature)

