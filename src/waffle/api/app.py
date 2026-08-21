from fastapi import FastAPI

from src.waffle.core.blockchain import Blockchain
from src.waffle.crypto.wallet import Wallet, load_wallets, save_wallet
from src.waffle.core.transaction import Transaction
from src.waffle.storage.database import Database
from src.waffle.network.node import NodeNetwork

app = FastAPI(title="Waffle Blockchain API")

database = Database()
blockchain = Blockchain(database)
wallets = load_wallets()
network = NodeNetwork()


@app.get("/")
def home():
    return {
        "name": "Waffle Blockchain",
        "status": "online",
    }


@app.get("/blockchain")
def get_blockchain():
    return {
        "blocks": len(blockchain.chain),
        "valid": blockchain.is_valid(),
    }


@app.get("/blocks")
def get_blocks():
    return {
        "blocks": [
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

@app.get("/balance/{address}")
def get_balance(address: str):
    return {
        "address": address,
        "balance": blockchain.get_balance(address),
    }

@app.post("/wallet")
def create_wallet():
    wallet = Wallet()
    wallets[wallet.address] = wallet
    save_wallet(wallets)
    return {
        "address": wallet.address,
        "message": "Wallet created successfully",
    }

@app.post("/mine/{miner_address}")
def mine(miner_address: str):
    block = blockchain.mine_pending_transactions(
        difficulty=4,
        miner_address=miner_address,
    )

    if block is None:
        return {
            "message": "No pending transactions",
        }

    return {
        "message": "Block mined successfully",
        "block_index": block.index,
        "miner": miner_address,
        "hash": block.stored_hash,
    }

@app.get("/status")
def status():
    return {
        "blocks": len(blockchain.chain),
        "pending_transactions": len(blockchain.pending_transactions),
        "valid": blockchain.is_valid(),
    }

@app.post("/transaction")
def create_transaction(sender: str, recipient: str, amount: float):
    if sender not in wallets:
        return {"error": "Sender wallet not found"}

    wallet = wallets[sender]
    transaction = Transaction(
        sender=sender,
        recipient=recipient,
        amount=amount,
    )
    transaction.signature = wallet.sign(transaction.message())

    try:
        blockchain.add_transaction(transaction, wallet)
    except ValueError as error:
        return {"error": str(error)}

    return {
        "message": "Transaction added",
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
    }


@app.get("/transactions/pending")
def get_pending_transactions():
    return {
        "count": len(blockchain.pending_transactions),
        "transactions": [
            {
                "sender": transaction.sender,
                "recipient": transaction.recipient,
                "amount": transaction.amount,
                "signature": transaction.signature,
            }
            for transaction in blockchain.pending_transactions
        ],
    }


@app.post("/network/nodes")
def add_network_node(address: str):
    network.add_node(address)
    return {
        "message": "Node added",
        "nodes": network.get_nodes(),
    }


@app.get("/network/nodes")
def get_network_nodes():
    return {
        "nodes": network.get_nodes(),
    }

@app.get("/network/chain")
def get_network_chain():
    return {
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

@app.post("/network/sync")
def sync_network():
    longest_chain = network.replace_chain(blockchain)

    if longest_chain is None:
        return {
            "message": "Blockchain is already up to date",
            "blocks": len(blockchain.chain),
        }

    return {
        "message": "Longer chain found",
        "blocks": len(longest_chain),
    }

@app.get("/currency")
def get_currency():
    issued = sum(
        transaction["amount"]
        for block in blockchain.chain
        for transaction in block.data.get("transactions", [])
        if transaction.get("sender") == "SYSTEM"
    )

    return {
        "name": "Waffle",
        "symbol": "WFL",
        "issued_supply": issued,
        "max_supply": 21_000_000.0,
    }
