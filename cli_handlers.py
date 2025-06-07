import mod1
from crowdfunding_platform import CrowdfundingPlatform

def display_menu():
    """Display the main menu"""
    print("\n🌾 FARMER CROWDFUNDING PLATFORM 🌾")
    print("1. Create Campaign")
    print("2. List Campaigns") 
    print("3. Approve Campaign (Admin)")
    print("4. Invest in Campaign")
    print("5. Release Escrow (Admin)")
    print("6. Cancel Escrow (Admin)")
    print("7. Check Wallet Balance")
    print("8. Exit")

def handle_create_campaign(platform):
    """Handle campaign creation"""
    farmer_name = input("Farmer name: ")
    project_title = input("Project title: ")
    description = input("Project description: ")
    funding_goal = int(input("Funding goal (XRP): "))
    platform.create_campaign(farmer_name, project_title, description, funding_goal)

def handle_approve_campaign(platform):
    """Handle campaign approval"""
    campaign_id = int(input("Campaign ID to approve: "))
    platform.approve_campaign(campaign_id)

def handle_investment(platform):
    """Handle investment in campaign"""
    campaign_id = int(input("Campaign ID to invest in: "))
    investor_seed = input("Your wallet seed (or press Enter for new wallet): ").strip()
    if not investor_seed:
        new_wallet = mod1.get_account('')
        investor_seed = new_wallet.seed
        print(f"New wallet created: {new_wallet.address}")
        print(f"Your seed (save this!): {investor_seed}")
    
    amount = int(input("Investment amount (XRP): "))
    platform.invest_in_campaign(campaign_id, investor_seed, amount)

def handle_check_balance(platform):
    """Handle balance checking"""
    wallet_seed = input("Wallet seed: ")
    platform.check_balances(wallet_seed)

def handle_release_escrow(platform):
    """Admin: Release escrow for investment"""
    inv_id = int(input("Investment ID to release escrow: "))
    admin_seed = input("Admin wallet seed: ")
    platform.release_escrow(inv_id, admin_seed)

def handle_cancel_escrow(platform):
    """Admin: Cancel escrow for investment"""
    inv_id = int(input("Investment ID to cancel escrow: "))
    admin_seed = input("Admin wallet seed: ")
    platform.cancel_escrow(inv_id, admin_seed)

def cli_handle():
    """Main CLI handler"""
    platform = CrowdfundingPlatform()
    
    while True:
        display_menu()
        choice = input("\nSelect option (1-8): ").strip()
        
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
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")