import xrpl
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import CredentialCreate
from xrpl.transaction import submit_and_wait
from xrpl.utils import str_to_hex

TESTNET_URL = "https://s.devnet.rippletest.net:51234"

def issue_crop_credential(issuer_seed, farmer_address, credential_type, uri=None, expiration=None):
    wallet = Wallet.from_seed(issuer_seed)
    client = JsonRpcClient(TESTNET_URL)

    tx_args = {
        "account": wallet.address,
        "subject": farmer_address,
        "credential_type": str_to_hex(credential_type),
    }
    if uri:
        tx_args["uri"] = str_to_hex(uri)
    if expiration:
        from xrpl.utils import datetime_to_ripple_time
        from datetime import datetime
        if isinstance(expiration, str):
            expiration = datetime.fromisoformat(expiration)
        tx_args["expiration"] = datetime_to_ripple_time(expiration)

    cred_tx = CredentialCreate(**tx_args)
    resp = submit_and_wait(cred_tx, client, wallet)
    return resp.result

def lookup_credentials(address, by="subject"):
    client = JsonRpcClient(TESTNET_URL)
    from xrpl.models.requests import AccountObjects, AccountObjectType
    req = AccountObjects(
        account=address,
        type=AccountObjectType.CREDENTIAL,
    )
    resp = client.request(req)
    return resp.result.get("account_objects", [])
