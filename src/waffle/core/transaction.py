from dataclasses import dataclass


TRANSACTION_FEE_RATE = 0.01


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    signature: str = ""

    @property
    def fee(self) -> float:
        return self.amount * TRANSACTION_FEE_RATE

    @property
    def total(self) -> float:
        return self.amount + self.fee

    def message(self) -> str:
        return f"{self.sender}:{self.recipient}:{self.amount}"

    def is_valid(self, wallet) -> bool:
        return wallet.verify(self.message(), self.signature)
