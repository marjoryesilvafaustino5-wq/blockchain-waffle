from src.waffle.core.blockchain import Blockchain
from src.waffle.crypto.wallet import Wallet
from src.waffle.storage.database import Database


def main():
    wallet = Wallet()
    blockchain = Blockchain()

    blockchain.add_block({
        "sender": wallet.address,
        "message": "Minha primeira blockchain Waffle!",
    })

    database = Database()
    database.save(blockchain)

    print("=== Blockchain Waffle ===")
    print("Carteira:", wallet.address)
    print("Blocos:", len(blockchain.chain))
    print("Blockchain válida:", blockchain.is_valid())
    print("Blockchain salva em:", database.filename)


if __name__ == "__main__":
    main()
