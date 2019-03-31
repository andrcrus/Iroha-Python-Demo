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
