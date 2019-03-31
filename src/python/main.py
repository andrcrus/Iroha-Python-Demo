from flask import Flask, jsonify, make_response, render_template, request

from src.python import config
from src.python.Sawmill import Sawmill
from src.python.ledger import Ledger

app = Flask(__name__)

ledger = Ledger(None)
sawmill_names = list(map(config.to_lower_case_only_letters, config.sawmill_names))
sawmills = [Sawmill(name, ledger.domain_name, ledger) for name in sawmill_names]
ledger.sawmills = sawmills
history = []

sawmills_by_name = dict(zip(sawmill_names, sawmills))


@app.route('/acc/<account_name>')
def get_account_info(account_name):
    sawmill = sawmills_by_name.get(account_name)
    if sawmill is None:
        return make_response(jsonify({"error": "account is not found"}), 404)
    return jsonify({account_name: sawmill.get_cattle()})


@app.route('/admin_details')
def admin_details():
    return ledger.get_admin_details()


@app.route('/send', methods=['get'])
def get_send_page():
    return render_template('send_form.html', assets_items=ledger.get_accounts_info(), assets=ledger.woods,
                           accountsFrom=sawmill_names, accountsTo=sawmill_names, history=history)


@app.route('/send', methods=['post'])
def transfer_wood():
    accountFrom = sawmills_by_name.get(request.form.get("accountFrom"))
    if accountFrom is None:
        return make_response(jsonify({"error": "account is not found."}), 404)
    accountTo = sawmills_by_name.get(request.form.get("accountTo"))
    if accountFrom is None:
        return make_response(jsonify({"error": "account is not found."}), 404)
    if accountTo.full_name == accountFrom.full_name:
        return make_response(jsonify({"error": "accounts are equals."}), 403)
    asset = request.form.get("asset")
    if asset not in ledger.woods:
        return make_response(jsonify({"error": "wood is not exists."}), 403)
    amount = request.form.get("amount")
    if amount == '':
        return make_response(jsonify({"error": "You must define amount."}), 403)

    if int(amount) > int(accountFrom.get_cattle()[asset]):
        history.append(f'{accountFrom.account_name} -> {accountTo.account_name}: {amount} of {asset} !NOT VALID!;')
        return make_response(jsonify({"error": "Oops...You have no resources..."}), 403)
    result = accountFrom.transfer_wood(accountTo.account_name, asset, int(amount))
    result = ','.join([str(r) for r in result])
    history.append(f'{accountFrom.account_name} -> {accountTo.account_name}: {amount} of {asset};')
    return jsonify({"Status": result})


if __name__ == '__main__':
    ledger.init_ledger()
    app.run('0.0.0.0')
