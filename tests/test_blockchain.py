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

def test_invalid_mining_reward():
    wallet = Wallet()
    blockchain = Blockchain()

    block = blockchain.add_block({
        "transactions": [{
            "sender": "SYSTEM",
            "recipient": wallet.address,
            "amount": 1000.0,
            "signature": "",
        }]
    })
    blockchain.mine_block(block, difficulty=4)

    assert blockchain.is_valid() is False


def test_database_save_and_load(tmp_path):
    from src.waffle.storage.database import Database

    blockchain = Blockchain()
    database = Database(tmp_path / "waffle_chain.json")

    database.save(blockchain)

    loaded = database.load()

    assert len(loaded) == 1
    assert loaded[0]["index"] == 0
    assert loaded[0]["data"] == {"message": "Genesis Block"}

def test_currency_supply():
    from src.waffle.core.blockchain import Blockchain

    blockchain = Blockchain()

    block = blockchain.mine_pending_transactions(
        miner_address="miner-test"
    )

    supply = sum(
        transaction["amount"]
        for block in blockchain.chain
        for transaction in block.data.get("transactions", [])
        if transaction.get("sender") == "SYSTEM"
    )

    assert supply == 50.0
    assert block.data["transactions"][-1]["recipient"] == "miner-test"

def test_transaction_negative_amount():
    wallet = Wallet()
    blockchain = Blockchain()

    transaction = Transaction(wallet.address, "Bob", -10)
    transaction.signature = wallet.sign(transaction.message())

    try:
        blockchain.add_transaction(transaction, wallet)
    except ValueError as error:
        assert str(error) == "Invalid transaction amount"
    else:
        assert False


def test_transaction_fee():
    wallet = Wallet()
    transaction = Transaction(wallet.address, "Bob", 10)

    assert transaction.fee == 0.1
    assert transaction.total == 10.1


def test_fee_balance_after_mining():
    wallet = Wallet()
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

    transaction = Transaction(wallet.address, "Bob", 10)
    transaction.signature = wallet.sign(transaction.message())

    blockchain.add_transaction(transaction, wallet)
    blockchain.mine_pending_transactions(
        difficulty=4,
        miner_address=wallet.address,
    )

    assert blockchain.get_fee_balance() == 0.1


def test_pending_transactions_cannot_overspend():
    wallet = Wallet()
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

    transaction1 = Transaction(wallet.address, "Bob", 30)
    transaction1.signature = wallet.sign(transaction1.message())

    transaction2 = Transaction(wallet.address, "Carol", 20)
    transaction2.signature = wallet.sign(transaction2.message())

    blockchain.add_transaction(transaction1, wallet)

    try:
        blockchain.add_transaction(transaction2, wallet)
    except ValueError as error:
        assert str(error) == "Insufficient balance"
    else:
        assert False


def test_network_accepts_longer_valid_chain(monkeypatch, tmp_path):
    from src.waffle.network.node import NodeNetwork

    blockchain = Blockchain()
    database = Database(tmp_path / "chain.json")
    blockchain.database = database

    funding_block = blockchain.add_block({
        "transactions": [{
            "sender": "SYSTEM",
            "recipient": "miner-test",
            "amount": 50.0,
            "signature": "",
        }]
    })
    blockchain.mine_block(funding_block, difficulty=4)

    network = NodeNetwork(tmp_path / "nodes.json")
    network.nodes.add("http://fake-node:8000")

    response_data = {
        "chain": [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.stored_hash,
            }
            for block in blockchain.chain
        ]
    }

    class FakeResponse:
        status_code = 200

        def json(self):
            return response_data

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)

    local_blockchain = Blockchain()
    result = network.replace_chain(local_blockchain)

    assert result is not None
    assert len(result) == 2
    assert len(local_blockchain.chain) == 2


def test_network_rejects_invalid_chain():
    from src.waffle.network.node import NodeNetwork
    from src.waffle.core.block import Block

    network = NodeNetwork()

    blockchain = Blockchain()

    invalid_block = Block(
        index=1,
        timestamp=1,
        data={"message": "invalido"},
        previous_hash=blockchain.chain[0].hash(),
        nonce=0,
    )

    invalid_block.stored_hash = "0000invalid"

    assert network._is_valid_chain(
        [blockchain.chain[0], invalid_block]
    ) is False


def test_blockchain_state():
    from src.waffle.core.state import BlockchainState

    blockchain = Blockchain()
    state = BlockchainState(blockchain)

    assert state.get_balance("unknown-address") == 0.0
    assert state.get_fee_balance() == 0.0
