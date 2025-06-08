import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import TrustSet
from xrpl.utils import xrp_to_drops

TESTNET_URL = "https://s.devnet.rippletest.net:51234"

def prepare_trustset_tx(account_address, issuer_address, currency, limit_value):
    if len(currency) == 3:
        currency_code = currency.upper()
    else:
        raise ValueError("Currency must be a 3-character code (e.g. 'USD', 'ABC').")
    trustset_tx = TrustSet(
        account=account_address,
        limit_amount={
            "currency": currency_code,
            "issuer": issuer_address,
            "value": str(limit_value)
        },
    )
    client = JsonRpcClient(TESTNET_URL)
    from xrpl.transaction import autofill
    autofilled = autofill(trustset_tx, client)
    return autofilled.to_xrpl()

def get_trustlines(address):
    from xrpl.models.requests import AccountLines
    client = JsonRpcClient(TESTNET_URL)
    req = AccountLines(account=address, ledger_index="validated")
    resp = client.request(req)
    return resp.result.get("lines", [])