from iroha import Iroha, IrohaGrpc, IrohaCrypto
from iroha.primitive_pb2 import can_set_my_account_detail, can_receive, can_transfer

import binascii
from random import randint
from itertools import product

from src.python import config


class Ledger:
    def __init__(self):
        self.domain_name = "sawmill"
        self.admin_private_key = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'
        self.iroha = Iroha('admin@test')
        self.net = IrohaGrpc()

        self.woods = list(map(config.to_lower_case_only_letters, config.woods))  # uses as assets
        self.commands = [
            self.iroha.command('CreateDomain', domain_id=self.domain_name, default_role='user'),
            *[self.iroha.command('CreateAsset', asset_name=wood,
                                 domain_id=self.domain_name, precision=0)
              for wood in self.woods]
        ]
        tx = IrohaCrypto.sign_transaction(
            self.iroha.transaction(self.commands), self.admin_private_key)
        print(self.send_transaction_and_print_status(tx))
        self.get_admin_details()
        tx = self.iroha.transaction(
            [self.iroha.command('AddAssetQuantity', asset_id=f'{wood}#{self.domain_name}', amount='100')
             for wood in self.woods]
        )
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_print_status(tx))
        self.get_admin_details()

    def send_transaction_and_print_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        return list(self.net.tx_status_stream(transaction))

    def get_admin_details(self):
        query = self.iroha.query('GetAccountAssets', account_id=f'admin@test')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(
                asset.asset_id, asset.balance))

    def init(self, sawmills):
        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name=sawmill.account_name, domain_id=sawmill.domain,
                               public_key=sawmill.public_key)
            for sawmill in sawmills
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_print_status(tx))

        print("=" * 20)
        tx_commands = []
        for i in sawmills:
            for j in self.woods:
                print(f"{i.account_name}: {j}")
                tx_commands.append(self.iroha.command('TransferAsset', src_account_id='admin@test',
                                                      dest_account_id=f'{i.account_name}@{self.domain_name}',
                                                      asset_id=f'{j}#{self.domain_name}',
                                                      amount=str(randint(1, 10))))
        print("=" * 20)
        tx = self.iroha.transaction(tx_commands)
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_print_status(tx))
        self.get_admin_details()
        print("=" * 20)
        for i in sawmills:
            print(f'{i.account_name}: {i.get_cattle()}')
