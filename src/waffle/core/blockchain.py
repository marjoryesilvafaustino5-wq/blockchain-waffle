from .block import Block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(
            index=0,
            timestamp=0,
            data={"message": "Genesis Block"},
            previous_hash="0",
        )

    def add_block(self, data):
        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=__import__("time").time(),
            data=data,
            previous_hash=previous_block.hash(),
        )

        self.chain.append(new_block)
        return new_block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.previous_hash != previous.hash():
                return False

        return True
