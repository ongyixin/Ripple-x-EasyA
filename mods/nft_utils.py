import xrpl
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import NFTokenMint, NFTokenBurn, NFTokenCreateOffer, NFTokenAcceptOffer
from xrpl.models.requests import AccountNFTs
from xrpl.transaction import submit_and_wait

TESTNET_URL = "https://s.devnet.rippletest.net:51234"

def mint_nft(seed, uri, taxon=0):
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(TESTNET_URL)
    mint_tx = NFTokenMint(
        account=wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=8, # transferable
        nftoken_taxon=taxon,
    )
    tx_response = submit_and_wait(mint_tx, client, wallet)
    nft_id = None
    if "meta" in tx_response.result and "nftokens" in tx_response.result["meta"]:
        # parse the created NFT ID from meta
        for node in tx_response.result["meta"]["nftokens"]:
            if node["ModifiedNode"]["LedgerEntryType"] == "NFTokenPage":
                if "PreviousFields" not in node["ModifiedNode"]: # just minted
                    nft_id = node["ModifiedNode"]["FinalFields"]["NFTokens"][-1]["NFToken"]["NFTokenID"]
    # fallback: fetch all NFTs for account and get the latest
    if not nft_id:
        nfts = get_nfts(wallet.seed)
        if nfts:
            nft_id = nfts[-1]['NFTokenID']
    return nft_id, tx_response.result

def get_nfts(seed):
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(TESTNET_URL)
    nfts = []
    req = AccountNFTs(account=wallet.address)
    resp = client.request(req)
    if "account_nfts" in resp.result:
        nfts = resp.result["account_nfts"]
    return nfts

def transfer_nft(owner_seed, dest_address, nft_id):
    wallet = Wallet.from_seed(owner_seed)
    client = JsonRpcClient(TESTNET_URL)
    offer_tx = NFTokenCreateOffer(
        account=wallet.address,
        nftoken_id=nft_id,
        amount="0", # 0 is equivalent to gift
        destination=dest_address,
        flags=1 # sell offer
    )
    offer_resp = submit_and_wait(offer_tx, client, wallet)
    offer_id = offer_resp.result['hash']
    return offer_resp.result

def burn_nft(owner_seed, nft_id):
    wallet = Wallet.from_seed(owner_seed)
    client = JsonRpcClient(TESTNET_URL)
    burn_tx = NFTokenBurn(
        account=wallet.address,
        nftoken_id=nft_id,
    )
    burn_resp = submit_and_wait(burn_tx, client, wallet)
    return burn_resp.result
