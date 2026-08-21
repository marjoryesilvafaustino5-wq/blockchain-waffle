from src.waffle.core.blockchain import Blockchain
from src.waffle.core.transaction import Transaction
from src.waffle.crypto.wallet import Wallet
from src.waffle.storage.database import Database


def test_blockchain():
    blockchain = Blockchain()

    assert len(blockchain.chain) == 1
    assert blockchain.is_valid() is True


def test_add_block():
    blockchain = Blockchain()

    block = blockchain.add_block({"message": "Teste"})
    blockchain.mine_block(block, difficulty=4)

    assert len(blockchain.chain) == 2
    assert blockchain.is_valid() is True


def test_wallet():
    wallet = Wallet()

    assert wallet.address
    assert len(wallet.address) == 40


def test_database(tmp_path):
    blockchain = Blockchain()
    blockchain.add_block({"message": "Teste de armazenamento"})

    database = Database(tmp_path / "chain.json")
    database.save(blockchain)

    loaded = database.load()

    assert len(loaded) == 2

def test_detect_tampered_block():
    blockchain = Blockchain()

    block = blockchain.add_block({"message": "Seguro"})
    blockchain.mine_block(block, difficulty=4)

    assert blockchain.is_valid() is True

    block.data = {"message": "ALTERADO"}

    assert blockchain.is_valid() is False

def test_unmined_block_is_invalid():
    blockchain = Blockchain()

    blockchain.add_block({"message": "Nao minerado"})

    assert blockchain.is_valid() is False

def test_transaction_signature():
    wallet = Wallet()
    transaction = Transaction(wallet.address, "Bob", 10)

    transaction.signature = wallet.sign(transaction.message())

    assert transaction.is_valid(wallet) is True

def test_invalid_transaction_signature():
    wallet = Wallet()
    transaction = Transaction(wallet.address, "Bob", 10)

    transaction.signature = "assinatura_invalida"

    assert transaction.is_valid(wallet) is False

def test_mine_pending_transactions():
    wallet = Wallet()
    transaction = Transaction(wallet.address, "Bob", 10)
    transaction.signature = wallet.sign(transaction.message())

    blockchain = Blockchain()

    funding_block = blockchain.add_block({
        "transactions": [{
            "sender": "SYSTEM",
            "recipient": wallet.address,
            "amount": 50.0,
            "signature": "",
        }]
    })
    blockchain.mine_block(funding_block, difficulty=4)

    blockchain.add_transaction(transaction, wallet)

    assert len(blockchain.pending_transactions) == 1

    block = blockchain.mine_pending_transactions(difficulty=4)

    assert block is not None
    assert len(blockchain.pending_transactions) == 0
    assert len(blockchain.chain) == 3
    assert blockchain.is_valid() is True

def test_transaction_insufficient_balance():
    wallet = Wallet()
    blockchain = Blockchain()

    transaction = Transaction(wallet.address, "Bob", 10)
    transaction.signature = wallet.sign(transaction.message())

    try:
        blockchain.add_transaction(transaction, wallet)
    except ValueError as error:
        assert str(error) == "Insufficient balance"
    else:
        assert False
