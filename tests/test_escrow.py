from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.transaction import submit_and_wait
from xrpl.models.requests import Tx
import time

client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
investor = generate_faucet_wallet(client)
farmer = generate_faucet_wallet(client)

print("Investor:", investor.address)
print("Farmer:", farmer.address)

# create escrow (finish_after in 5 seconds)
escrow_tx = EscrowCreate(
    account=investor.classic_address,
    amount="10000000",  # 10 XRP in drops
    destination=farmer.classic_address,
    finish_after=int(time.time()) + 5
)

print("Creating escrow...")
escrow_resp = submit_and_wait(escrow_tx, client, investor)
escrow_tx_hash = escrow_resp.result["hash"]
escrow_seq = escrow_resp.result["Sequence"]

print("Escrow Create Response:")
print(escrow_resp)

print("Waiting for escrow finish...")
time.sleep(7)  # wait for finish_after time to pass

# finish escrow
finish_tx = EscrowFinish(
    account=investor.classic_address,
    owner=investor.classic_address,
    offer_sequence=escrow_seq
)
finish_resp = submit_and_wait(finish_tx, client, investor)
finish_tx_hash = finish_resp.result["hash"]

print("Escrow Finish Response:")
print(finish_resp)

# check both txs on the ledger
for tx_hash, label in [(escrow_tx_hash, "EscrowCreate"), (finish_tx_hash, "EscrowFinish")]:
    tx_req = Tx(transaction=tx_hash)
    tx_resp = client.request(tx_req)
    print(f"{label} TX validation:")
    print(tx_resp)