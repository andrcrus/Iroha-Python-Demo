from random import randint

from flask import Flask
from iroha import IrohaCrypto

from src.python import config
from src.python.Sawmill import Sawmill
from src.python.ledger import Ledger

app = Flask(__name__)

ledger = Ledger()
sawmill_names = list(map(config.to_lower_case_only_letters, config.sawmill_names))
sawmills = [Sawmill(name, ledger.domain_name, ledger) for name in sawmill_names]


if __name__ == '__main__':
    ledger.init(sawmills)
    app.run('0.0.0.0')
