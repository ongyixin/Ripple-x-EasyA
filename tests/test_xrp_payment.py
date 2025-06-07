from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.models.requests import Tx
from xrpl.utils import xrp_to_drops
import time

client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
sender = generate_faucet_wallet(client)
receiver = generate_faucet_wallet(client)

print("Sender:", sender.address)
print("Receiver:", receiver.address)

# Send 5 XRP
payment = Payment(
    account=sender.classic_address,
    amount=xrp_to_drops(5),
    destination=receiver.classic_address
)

print("Sending XRP payment...")
response = submit_and_wait(payment, client, sender)
payment_hash = response.result["hash"]

print("Payment Response:")
print(response)

print("Waiting for validation...")
time.sleep(4)

tx_req = Tx(transaction=payment_hash)
tx_resp = client.request(tx_req)
print("XRP Payment Transaction Status:")
print(tx_resp)