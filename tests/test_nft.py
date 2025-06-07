from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import NFTokenMint
from xrpl.transaction import submit_and_wait
from xrpl.utils import str_to_hex
from xrpl.models.requests import Tx
import time

client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
wallet = generate_faucet_wallet(client)

print(f"Wallet: {wallet.address}")

mint_tx = NFTokenMint(
    account=wallet.classic_address,
    uri=str_to_hex("https://example.com/nft-metadata"),
    flags=8,
    nftoken_taxon=0
)

print("Minting NFT...")
response = submit_and_wait(mint_tx, client, wallet)
print("NFT Mint Response:")
print(response)
mint_tx_hash = response.result["hash"]

print("Waiting for validation...")
time.sleep(4)

tx_req = Tx(transaction=mint_tx_hash)
tx_resp = client.request(tx_req)
print("NFT Mint Transaction Status:")
print(tx_resp)