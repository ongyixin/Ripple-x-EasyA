import xrpl
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
from datetime import datetime, timedelta

TESTNET_URL = "https://s.devnet.rippletest.net:51234"

def create_escrow(seed, amount_xrp, destination, finish_after_sec=60):
    """
    Locks XRP in escrow. By default, unlocks after 60s (change for production!).
    Returns escrow sequence (needed to finish/cancel).
    """
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(TESTNET_URL)
    finish_after = int((datetime.utcnow() + timedelta(seconds=finish_after_sec) - datetime(2000, 1, 1)).total_seconds())
    escrow_tx = EscrowCreate(
        account=wallet.address,
        amount=xrp_to_drops(amount_xrp),
        destination=destination,
        finish_after=finish_after,
    )
    tx_response = submit_and_wait(escrow_tx, client, wallet)
    sequence = tx_response.result['Sequence'] if 'Sequence' in tx_response.result else escrow_tx.sequence
    tx_hash = tx_response.result['hash']
    return {"sequence": sequence, "tx_hash": tx_hash, "finish_after": finish_after}

def finish_escrow(seed, owner, sequence):
    """
    Releases escrow funds to destination. Only callable after finish_after time.
    """
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(TESTNET_URL)
    finish_tx = EscrowFinish(
        account=wallet.address,
        owner=owner,
        offer_sequence=sequence,
    )
    tx_response = submit_and_wait(finish_tx, client, wallet)
    return tx_response.result

def cancel_escrow(seed, owner, sequence):
    """
    Cancels escrow, refunds funds to sender (if cancel time is allowed).
    """
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(TESTNET_URL)
    cancel_tx = EscrowCancel(
        account=wallet.address,
        owner=owner,
        offer_sequence=sequence,
    )
    tx_response = submit_and_wait(cancel_tx, client, wallet)
    return tx_response.result