import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import (
    NFTokenMint,
    NFTokenBurn,
    NFTokenCreateOffer,
    NFTokenAcceptOffer,
)
from xrpl.models.requests import AccountNFTs
from xrpl.utils import str_to_hex
from xrpl.transaction import autofill

TESTNET_URL = "https://s.devnet.rippletest.net:51234"

def prepare_nft_mint_tx(account_address, uri, taxon=0):
    mint_tx = NFTokenMint(
        account=account_address,
        uri=str_to_hex(uri),
        flags=8, # Transferable
        nftoken_taxon=taxon,
    )
    client = JsonRpcClient(TESTNET_URL)
    autofilled = autofill(mint_tx, client)
    return autofilled.to_xrpl()

def get_nfts_for_address(address):
    client = JsonRpcClient(TESTNET_URL)
    req = AccountNFTs(account=address)
    resp = client.request(req)
    return resp.result.get("account_nfts", [])

def prepare_nft_transfer_tx(owner_address, dest_address, nft_id):
    # Create an offer to give (sell for 0) the NFT to the dest_address
    offer_tx = NFTokenCreateOffer(
        account=owner_address,
        nftoken_id=nft_id,
        amount="0", # 0 XRP = free transfer
        destination=dest_address,
    )
    client = JsonRpcClient(TESTNET_URL)
    autofilled = autofill(offer_tx, client)
    return autofilled.to_xrpl()

def prepare_nft_burn_tx(owner_address, nft_id):
    burn_tx = NFTokenBurn(
        account=owner_address,
        nftoken_id=nft_id,
    )
    client = JsonRpcClient(TESTNET_URL)
    autofilled = autofill(burn_tx, client)
    return autofilled.to_xrpl()