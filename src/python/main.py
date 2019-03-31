from itertools import product
from random import randint
from iroha import IrohaCrypto

from src.python.Sawmill import Sawmill
from src.python.ledger import Ledger

ledger = Ledger()
sawmill_names = ["LenLesSrubPro", "LESORUBKA", "greatest", "Default name"]
sawmills = [Sawmill(name, ledger.domain_name, ledger) for name in sawmill_names]


def init():
    tx = ledger.iroha.transaction([
        ledger.iroha.command('CreateAccount', account_name=sawmill.account_name, domain_id=sawmill.domain,
                             public_key=sawmill.public_key)
        for sawmill in sawmills
    ])
    IrohaCrypto.sign_transaction(tx, ledger.admin_private_key)
    ledger.send_transaction_and_print_status(tx)

    tx = ledger.iroha.transaction([
        ledger.iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id=f'{name}@{domain_name}',
                             asset_id=f'{asset}#{ledger.domain_name}', amount=str(randint(1, 10)))
        for asset, name in product(ledger.woods, sawmill_names)
    ])
    IrohaCrypto.sign_transaction(tx, ledger.admin_private_key)
    ledger.send_transaction_and_print_status(tx)
    ledger.get_admin_details()


if __name__ == '__main__':
    pass
