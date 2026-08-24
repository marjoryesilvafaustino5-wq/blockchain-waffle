import argparse

from src.waffle.core.blockchain import Blockchain
from src.waffle.core.transaction import Transaction
from src.waffle.crypto.wallet import Wallet, load_wallets, save_wallet
from src.waffle.storage.database import Database


def get_blockchain():
    return Blockchain(Database())


def create_wallet():
    wallets = load_wallets()
    wallet = Wallet()

    wallets[wallet.address] = wallet
    save_wallet(wallets)

    print("=== Waffle Wallet ===")
    print("Carteira criada:")
    print(wallet.address)
    print()
    print("Guarde sua carteira com segurança.")


def show_balance(address):
    blockchain = get_blockchain()
    balance = blockchain.get_balance(address)

    print("=== Waffle Balance ===")
    print("Endereço:", address)
    print("Saldo:", balance, "WFL")


def show_status():
    blockchain = get_blockchain()

    print("=== Waffle Blockchain ===")
    print("Blocos:", len(blockchain.chain))
    print("Transações pendentes:", len(blockchain.pending_transactions))
    print("Blockchain válida:", blockchain.is_valid())
    print("Taxas acumuladas:", blockchain.get_fee_balance(), "WFL")


def mine(miner_address):
    blockchain = get_blockchain()

    block = blockchain.mine_pending_transactions(
        difficulty=4,
        miner_address=miner_address,
    )

    print("=== Waffle Mining ===")
    print("Bloco:", block.index)
    print("Minerador:", miner_address)
    print("Recompensa processada.")
    print("Hash:", block.stored_hash)


def send(sender, recipient, amount):
    wallets = load_wallets()

    if sender not in wallets:
        print("Erro: carteira do remetente não encontrada.")
        return

    wallet = wallets[sender]
    blockchain = get_blockchain()

    transaction = Transaction(
        sender=sender,
        recipient=recipient,
        amount=amount,
    )

    transaction.signature = wallet.sign(transaction.message())

    try:
        blockchain.add_transaction(transaction, wallet)
    except ValueError as error:
        print("Erro:", error)
        return

    print("=== Waffle Transaction ===")
    print("Remetente:", sender)
    print("Destinatário:", recipient)
    print("Valor:", amount, "WFL")
    print("Taxa:", transaction.fee, "WFL")
    print("Total:", transaction.total, "WFL")
    print("Transação adicionada à fila.")


def main():
    parser = argparse.ArgumentParser(
        prog="waffle",
        description="Waffle Blockchain CLI",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "wallet",
        help="Criar uma nova carteira",
    )

    balance_parser = subparsers.add_parser(
        "balance",
        help="Consultar saldo",
    )
    balance_parser.add_argument("address")

    send_parser = subparsers.add_parser(
        "send",
        help="Criar uma transação",
    )
    send_parser.add_argument("sender")
    send_parser.add_argument("recipient")
    send_parser.add_argument("amount", type=float)

    mine_parser = subparsers.add_parser(
        "mine",
        help="Minerar transações pendentes",
    )
    mine_parser.add_argument("address")

    subparsers.add_parser(
        "status",
        help="Mostrar status da blockchain",
    )

    args = parser.parse_args()

    if args.command == "wallet":
        create_wallet()
    elif args.command == "balance":
        show_balance(args.address)
    elif args.command == "send":
        send(args.sender, args.recipient, args.amount)
    elif args.command == "mine":
        mine(args.address)
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
