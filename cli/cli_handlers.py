from src.crowdfunding_platform import CrowdfundingPlatform
from mods.credential_utils import issue_crop_credential, lookup_credentials
from mods.nft_batch import batch_mint
from mods.wallet import get_iou_balances
from mods.nft_utils import (
    get_nfts_for_address,  
    prepare_nft_transfer_tx, 
    prepare_nft_burn_tx,
)
import json

def display_menu():
    print("\n🌾 FARMER CROWDFUNDING PLATFORM 🌾")
    print("1. Create Campaign")
    print("2. List Campaigns") 
    print("3. Approve Campaign (Admin)")
    print("4. Invest in Campaign")
    print("5. Release Escrow (Admin)")
    print("6. Cancel Escrow (Admin)")
    print("7. Check Wallet Balance")
    print("8. View My NFTs")
    print("9. Transfer My NFT")
    print("10. Burn My NFT")
    print("11. Submit Crop Credential (Admin/Oracle)")
    print("12. View Credentials for Address")
    print("13. Invest via Check")
    print("14. Batch Mint NFTs")
    print("15. Check IOU Balances")
    print ("16. Display Trustlines")
    print("17. Exit")

def handle_create_campaign(platform):
    farmer_name = input("Farmer name: ")
    project_title = input("Project title: ")
    description = input("Project description: ")
    funding_goal = int(input("Funding goal (XRP): "))
    farmer_address = input("Farmer XRPL public address: ").strip()
    platform.create_campaign(farmer_name, project_title, description, funding_goal, farmer_address)

def handle_approve_campaign(platform):
    campaign_id = int(input("Campaign ID to approve: "))
    platform.approve_campaign(campaign_id)

def handle_investment(platform):
    campaign_id = int(input("Campaign ID to invest in: "))
    investor_address = input("Your XRPL public address: ").strip()
    amount = int(input("Investment amount (XRP): "))
    platform.invest_in_campaign(campaign_id, investor_address, amount)
    print("\nPlease sign and submit the displayed unsigned transactions using your wallet (e.g., XUMM, browser extension).")

def handle_check_balance(platform):
    wallet_address = input("Wallet XRPL address: ")
    platform.check_balances(wallet_address)

def handle_release_escrow(platform):
    inv_id = int(input("Investment ID to release escrow: "))
    finisher_address = input("XRPL address (who will sign EscrowFinish): ")
    platform.provide_escrow_finish_instructions(inv_id, finisher_address)
    print("\nPlease sign and submit the displayed unsigned transaction using your wallet.")

def handle_cancel_escrow(platform):
    inv_id = int(input("Investment ID to cancel escrow: "))
    canceller_address = input("XRPL address (who will sign EscrowCancel): ")
    platform.provide_escrow_cancel_instructions(inv_id, canceller_address)
    print("\nPlease sign and submit the displayed unsigned transaction using your wallet.")

def handle_view_nfts():
    address = input("XRPL address to view NFTs: ")
    nfts = get_nfts_for_address(address)
    if not nfts:
        print("No NFTs found.")
    else:
        print("Your NFTs:")
        for i, nft in enumerate(nfts):
            from xrpl.utils import hex_to_str
            print(f"{i+1}) ID: {nft['NFTokenID']} | URI: {hex_to_str(nft['URI'])}")

def handle_transfer_nft():
    address = input("Your XRPL address: ")
    nfts = get_nfts_for_address(address)
    if not nfts:
        print("No NFTs found to transfer.")
        return
    for i, nft in enumerate(nfts):
        from xrpl.utils import hex_to_str
        print(f"{i+1}) ID: {nft['NFTokenID']} | URI: {hex_to_str(nft['URI'])}")
    idx = int(input("Select NFT number to transfer: ")) - 1
    dest = input("Destination XRPL address: ")
    nft_id = nfts[idx]['NFTokenID']
    tx = prepare_nft_transfer_tx(address, dest, nft_id)
    print("\nUnsigned NFT transfer transaction:")
    print(json.dumps(tx, indent=2))
    print("Sign and submit this transaction with your wallet (e.g., XUMM, browser extension).")

def handle_burn_nft():
    address = input("Your XRPL address: ")
    nfts = get_nfts_for_address(address)
    if not nfts:
        print("No NFTs found to burn.")
        return
    for i, nft in enumerate(nfts):
        from xrpl.utils import hex_to_str
        print(f"{i+1}) ID: {nft['NFTokenID']} | URI: {hex_to_str(nft['URI'])}")
    idx = int(input("Select NFT number to burn: ")) - 1
    nft_id = nfts[idx]['NFTokenID']
    tx = prepare_nft_burn_tx(address, nft_id)
    print("\nUnsigned NFT burn transaction:")
    print(json.dumps(tx, indent=2))
    print("Sign and submit this transaction with your wallet (e.g., XUMM, browser extension).")

def handle_submit_crop_credential():
    # ADMIN/ORACLE ONLY
    issuer_seed = input("Issuer (admin/oracle) seed: ")
    farmer_address = input("Farmer XRPL address: ")
    cred_type = input("Credential type (e.g. CropHealthy20240610): ")
    uri = input("Evidence URI (optional, or leave blank): ")
    if uri.strip() == "":
        uri = None
    expiration = input("Expiration datetime (YYYY-MM-DD or leave blank): ")
    if expiration.strip() == "":
        expiration = None
    result = issue_crop_credential(issuer_seed, farmer_address, cred_type, uri, expiration)
    print("Credential issued! TX result:")
    print(result)

def handle_view_credentials():
    address = input("XRPL address to view credentials for: ")
    creds = lookup_credentials(address, by="subject")
    if not creds:
        print("No credentials found.")
        return
    print("Credentials found:")
    for c in creds:
        from xrpl.utils import hex_to_str
        print(f"- Type: {hex_to_str(c['CredentialType'])}")
        if 'URI' in c:
            print(f"  URI: {hex_to_str(c['URI'])}")
        if 'Issuer' in c:
            print(f"  Issuer: {c['Issuer']}")
        if 'Expiration' in c:
            from xrpl.utils import ripple_time_to_datetime
            print(f"  Expiration: {ripple_time_to_datetime(c['Expiration'])}")
        print()

def handle_invest_via_check():
    # ADMIN/ADVANCED ONLY (non-standard user flow)
    seed = input("Backer wallet seed: ")
    amount = input("Amount: ")
    dest = input("Farmer address: ")
    currency = input("Currency (e.g., XRP): ")
    issuer = input("Issuer address (leave blank for XRP): ")
    if not issuer:
        issuer = None
    resp = send_check(seed, amount, dest, currency, issuer)
    print("Check sent. Result:")
    print(resp)

def handle_batch_nft_mint():
    # ADMIN/ADVANCED ONLY
    seed = input("Minter wallet seed: ")
    uri = input("NFT metadata URI: ")
    flags = input("Flags (usually 8 for transferable): ")
    fee = input("Transfer fee (e.g., 0): ")
    taxon = input("NFT Taxon (category code, e.g., 0): ")
    count = input("How many NFTs?: ")
    resp = batch_mint(seed, uri, flags, fee, taxon, count)
    print(resp)

def handle_check_iou_balances():
    address = input("XRPL Address to check IOU balances: ")
    ious = get_iou_balances(address)
    if not ious:
        print("No IOU balances found.")
    else:
        print("IOU Balances:")
        for iou in ious:
            print(f"{iou['currency']} issued by {iou['account']}: Balance {iou['balance']}")

def handle_display_trustlines(platform):
    address = input("XRPL address to display trustlines: ").strip()
    platform.display_trustlines(address)

def cli_handle():
    platform = CrowdfundingPlatform()
    while True:
        display_menu()
        choice = input("\nSelect option (1-17): ").strip()
        if choice == "1":
            handle_create_campaign(platform)
        elif choice == "2":
            platform.list_campaigns()
        elif choice == "3":
            handle_approve_campaign(platform)
        elif choice == "4":
            handle_investment(platform)
        elif choice == "5":
            handle_release_escrow(platform)
        elif choice == "6":
            handle_cancel_escrow(platform)
        elif choice == "7":
            handle_check_balance(platform)
        elif choice == "8":
            handle_view_nfts()
        elif choice == "9":
            handle_transfer_nft()
        elif choice == "10":
            handle_burn_nft()
        elif choice == "11":
            handle_submit_crop_credential()
        elif choice == "12":
            handle_view_credentials()
        elif choice == "13":
            handle_invest_via_check()
        elif choice == "14":
            handle_batch_nft_mint()
        elif choice == "15":
            handle_check_iou_balances()
        elif choice == "16":
            handle_display_trustlines(platform)
        elif choice == "17":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")