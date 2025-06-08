
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.models.requests import AccountObjects, Tx
from xrpl.transaction import submit_and_wait
from xrpl.utils import datetime_to_ripple_time, xrp_to_drops, drops_to_xrp, ripple_time_to_datetime
from datetime import datetime, timedelta
from os import urandom
from cryptoconditions import PreimageSha256

testnet_url = "https://s.altnet.rippletest.net:51234"

def generate_condition():
    """Generate a condition and fulfillment for escrows"""
    secret = urandom(32)
    fulfillment = PreimageSha256(preimage=secret)
    return (fulfillment.condition_binary.hex().upper(),
            fulfillment.serialize_binary().hex().upper())

def add_seconds(numOfSeconds):
    """Add seconds to current time and return in Ripple time format"""
    new_date = datetime.now()
    if new_date != '':
        new_date = datetime_to_ripple_time(new_date)
        new_date = new_date + int(numOfSeconds)
    return new_date

def create_time_escrow(seed, amount, destination, finish, cancel):
    """Create a time-based escrow"""
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(testnet_url)
    finish_date = add_seconds(finish)
    cancel_date = add_seconds(cancel)

    escrow_tx = EscrowCreate(
        account=wallet.address,
        amount=amount,
        destination=destination,
        finish_after=finish_date,
        cancel_after=cancel_date
    ) 
    
    reply = ""
    try:
        response = submit_and_wait(escrow_tx, client, wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply

def create_conditional_escrow(seed, amount, destination, cancel, condition):
    """Create a conditional escrow"""
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(testnet_url)
    cancel_date = add_seconds(cancel)

    escrow_tx = EscrowCreate(
        account=wallet.address,
        amount=amount,
        destination=destination,
        cancel_after=cancel_date,
        condition=condition
    ) 
    
    reply = ""
    try:
        response = submit_and_wait(escrow_tx, client, wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply

def finish_time_escrow(seed, owner, sequence):
    """Finish a time-based escrow"""
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(testnet_url)
    finish_tx = EscrowFinish(
        account=wallet.address,
        owner=owner,
        offer_sequence=int(sequence)
    )
    
    reply = ""
    try:
        response = submit_and_wait(finish_tx, client, wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply

def finish_conditional_escrow(seed, owner, sequence, condition, fulfillment):
    """Finish a conditional escrow"""
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(testnet_url)
    finish_tx = EscrowFinish(
        account=wallet.address,
        owner=owner,
        offer_sequence=int(sequence),
        condition=condition,
        fulfillment=fulfillment
    )
    
    reply = ""
    try:
        response = submit_and_wait(finish_tx, client, wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply

def cancel_escrow(seed, owner, sequence):
    """Cancel an escrow"""
    wallet = Wallet.from_seed(seed)
    client = JsonRpcClient(testnet_url)
    cancel_tx = EscrowCancel(
        account=wallet.address,
        owner=owner,
        offer_sequence=int(sequence)
    )
    
    reply = ""
    try:
        response = submit_and_wait(cancel_tx, client, wallet)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        reply = f"Submit failed: {e}"
    return reply

def get_escrows(account):
    """Get all escrows for an account, formatted"""
    client = JsonRpcClient(testnet_url)
    
    all_escrows_dict = {} 
    sent_escrows = [] 
    received_escrows = []

    req = AccountObjects(
        account=account,
        ledger_index="validated",
        type="escrow"
    )
    response = client.request(req)
    escrows = response.result["account_objects"]

    for escrow in escrows:
        escrow_data = {} 
        if isinstance(escrow["Amount"], str):
            escrow_data["escrow_id"] = escrow["index"]
            escrow_data["sender"] = escrow["Account"] 
            escrow_data["receiver"] = escrow["Destination"] 
            escrow_data["amount"] = str(drops_to_xrp(escrow["Amount"])) 
            if "PreviousTxnID" in escrow:
                escrow_data["prev_txn_id"] = escrow["PreviousTxnID"] 
            if "FinishAfter" in escrow:
                escrow_data["redeem_date"] = str(ripple_time_to_datetime(escrow["FinishAfter"])) 
            if "CancelAfter" in escrow:
                escrow_data["expiry_date"] = str(ripple_time_to_datetime(escrow["CancelAfter"]))
            if "Condition" in escrow:
                escrow_data["condition"] = escrow["Condition"]
                
            # Sort escrows
            if escrow_data["sender"] == account:
                sent_escrows.append(escrow_data)
            else:
                received_escrows.append(escrow_data)

    all_escrows_dict["sent"] = sent_escrows
    all_escrows_dict["received"] = received_escrows
    return all_escrows_dict

def get_escrow_sequence(prev_txn_id):
    """Get escrow sequence from transaction ID"""
    client = JsonRpcClient(testnet_url)
    req = Tx(transaction=prev_txn_id) 
    response = client.request(req)
    result = response.result
    
    if "Sequence" in result:
        return result["Sequence"]
    elif "TicketSequence" in result:
        return result["TicketSequence"]
    return None