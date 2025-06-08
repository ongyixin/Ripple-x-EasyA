import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountLines

testnet_url = "https://s.devnet.rippletest.net:51234/"

def get_account_info(address):
    from xrpl.clients import JsonRpcClient
    from xrpl.models.requests.account_info import AccountInfo

    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    req = AccountInfo(
        account=address,
        ledger_index="validated",
        strict=True
    )
    response = client.request(req)
    if "account_data" in response.result:
        return response.result["account_data"]
    else:
        print(f"❌ XRPL account {address} not found or not funded yet.")
        return None

def send_xrp(seed, amount, destination):
    sending_wallet = xrpl.wallet.Wallet.from_seed(seed)
    client = xrpl.clients.JsonRpcClient(testnet_url)
    payment = xrpl.models.transactions.Payment(
        account=sending_wallet.address,
        amount=xrpl.utils.xrp_to_drops(int(amount)),
        destination=destination,
    )
    try:	
        response = xrpl.transaction.submit_and_wait(payment, client, sending_wallet)	
    except xrpl.transaction.XRPLReliableSubmissionException as e:	
        response = f"Submit failed: {e}"

    return response

def get_iou_balances(address):
    """
    Returns a list of all trust lines (IOU balances) for the given XRPL address.
    """
    client = JsonRpcClient(testnet_url)
    req = AccountLines(
        account=address,
        ledger_index="validated"
    )
    response = client.request(req)
    if "lines" in response.result:
        return response.result["lines"]
    return []