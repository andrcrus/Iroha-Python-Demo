from random import randint
from iroha import IrohaCrypto

from src.python import config
from src.python.Sawmill import Sawmill
from src.python.ledger import Ledger

ledger = Ledger()
sawmill_names = list(map(config.to_lower_case_only_letters, config.sawmill_names))
sawmills = [Sawmill(name, ledger.domain_name, ledger) for name in sawmill_names]


def init():
    tx = ledger.iroha.transaction([
        ledger.iroha.command('CreateAccount', account_name=sawmill.account_name, domain_id=sawmill.domain,
                             public_key=sawmill.public_key)
        for sawmill in sawmills
    ])
    IrohaCrypto.sign_transaction(tx, ledger.admin_private_key)
    print(ledger.send_transaction_and_print_status(tx))

    print("="*20)
    tx_commands = []
    for i in sawmills:
        for j in ledger.woods:
            print(f"{i.account_name}: {j}")
            tx_commands.append(ledger.iroha.command('TransferAsset', src_account_id='admin@test',
                                                    dest_account_id=f'{i.account_name}@{ledger.domain_name}',
                                                    asset_id=f'{j}#{ledger.domain_name}', amount=str(randint(1, 10))))
    print("=" * 20)
    tx = ledger.iroha.transaction(tx_commands)
    IrohaCrypto.sign_transaction(tx, ledger.admin_private_key)
    print(ledger.send_transaction_and_print_status(tx))
    ledger.get_admin_details()
    print("=" * 20)
    for i in sawmills:
        print(f'{i.account_name}: {i.get_cattle()}')


if __name__ == '__main__':
    init()
