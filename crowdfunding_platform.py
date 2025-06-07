import json
import os
from datetime import datetime
import mod1  # XRPL wallet functions
import mod2  # Token/currency functions  
from escrow_utils import create_escrow, finish_escrow, cancel_escrow

class CrowdfundingPlatform:
    def __init__(self):
        self.storage_file = 'storage.json'
        self.init_storage()
        
    def init_storage(self):
        """Initialize JSON storage for campaigns and investments"""
        if not os.path.exists(self.storage_file):
            initial_data = {
                'campaigns': [],
                'investments': [],
                'next_campaign_id': 1,
                'next_investment_id': 1
            }
            with open(self.storage_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            print("✅ Storage initialized")
        else:
            print("✅ Storage loaded")

    def load_data(self):
        """Load data from JSON file"""
        with open(self.storage_file, 'r') as f:
            return json.load(f)

    def save_data(self, data):
        """Save data to JSON file"""
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_campaign(self, farmer_name, project_title, description, funding_goal):
        """Create a new farmer campaign"""
        print(f"\n🚜 Creating campaign for {farmer_name}...")
        
        # Generate XRPL wallet for farmer
        farmer_wallet = mod1.get_account('')
        
        data = self.load_data()
        
        campaign = {
            'id': data['next_campaign_id'],
            'farmer_name': farmer_name,
            'project_title': project_title,
            'description': description,
            'funding_goal': funding_goal,
            'farmer_wallet_seed': farmer_wallet.seed,
            'farmer_address': farmer_wallet.address,
            'token_currency': None,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        data['campaigns'].append(campaign)
        data['next_campaign_id'] += 1
        self.save_data(data)
        
        campaign_id = campaign['id']
        print(f"✅ Campaign created with ID: {campaign_id}")
        print(f"   Farmer wallet: {farmer_wallet.address}")
        print(f"   Seed (keep safe): {farmer_wallet.seed}")
        
        return campaign_id

    def approve_campaign(self, campaign_id):
        """Approve campaign and mint project token"""
        data = self.load_data()
        
        campaign = None
        for c in data['campaigns']:
            if c['id'] == campaign_id:
                campaign = c
                break
        
        if not campaign:
            print("❌ Campaign not found")
            return
            
        farmer_name = campaign['farmer_name']
        project_title = campaign['project_title']
        farmer_seed = campaign['farmer_wallet_seed']
        
        print(f"\n🎯 Approving campaign: {project_title}")
        
        # Create token currency code (max 3 chars for standard currency)
        token_currency = project_title[:3].upper()
        
        # Configure farmer account for token issuance
        print("   Setting up farmer account...")
        mod2.configure_account(farmer_seed, True)
        
        # Update campaign status and token info
        campaign['status'] = 'approved'
        campaign['token_currency'] = token_currency
        
        self.save_data(data)
        
        print(f"✅ Campaign approved! Token currency: {token_currency}")

    def invest_in_campaign(self, campaign_id, investor_seed, investment_amount):
        """Invest XRP in a campaign and receive project tokens"""
        data = self.load_data()
        
        campaign = None
        for c in data['campaigns']:
            if c['id'] == campaign_id and c['status'] == 'approved':
                campaign = c
                break
        
        if not campaign:
            print("❌ Campaign not found or not approved")
            return
            
        farmer_seed = campaign['farmer_wallet_seed']
        farmer_address = campaign['farmer_address']
        token_currency = campaign['token_currency']
        
        investor_wallet = mod1.get_account(investor_seed)
        
        print(f"\n💰 Processing investment of {investment_amount} XRP...")
        
        # Step 1: Lock XRP in escrow (lockbox)
        print("   Locking XRP in escrow (lockbox)...")
        escrow_info = create_escrow(
            investor_seed,
            investment_amount,
            farmer_address,
            finish_after_sec=120  # For demo: escrow unlocks in 2 min
        )
        print(f"Escrow created. Tx hash: {escrow_info['tx_hash']}, Sequence: {escrow_info['sequence']}")
            
        # Step 2: Create trust line for investor to receive tokens
        print("   Creating trust line for tokens...")
        trust_result = mod2.create_trust_line(investor_seed, farmer_address, token_currency, investment_amount * 10)
        
        # Step 3: Send project tokens to investor
        print("   Sending project tokens...")
        token_amount = investment_amount  # 1:1 ratio for MVP
        token_result = mod2.send_currency(farmer_seed, investor_wallet.address, token_currency, token_amount)
        
        # Record investment
        investment = {
            'id': data['next_investment_id'],
            'campaign_id': campaign_id,
            'investor_address': investor_wallet.address,
            'amount': investment_amount,
            'token_id': None,
            'created_at': datetime.now().isoformat(),
            'escrow_sequence': escrow_info['sequence'],
            'escrow_owner': investor_wallet.address,
            'escrow_tx_hash': escrow_info['tx_hash']
        }
        
        data['investments'].append(investment)
        data['next_investment_id'] += 1
        self.save_data(data)
        
        print(f"✅ Investment successful!")
        print(f"   Received {token_amount} {token_currency} tokens")

    def list_campaigns(self):
        """List all campaigns"""
        data = self.load_data()
        campaigns = data['campaigns']
        
        print("\n📋 All Campaigns:")
        print("-" * 80)
        
        if not campaigns:
            print("No campaigns found.")
            return
        
        for campaign in sorted(campaigns, key=lambda x: x['created_at'], reverse=True):
            campaign_id = campaign['id']
            farmer_name = campaign['farmer_name']
            title = campaign['project_title']
            desc = campaign['description']
            goal = campaign['funding_goal']
            token = campaign['token_currency']
            status = campaign['status']
            created = campaign['created_at']
            
            print(f"ID: {campaign_id} | {title} by {farmer_name}")
            print(f"   Goal: {goal} XRP | Status: {status} | Token: {token or 'N/A'}")
            print(f"   Description: {desc}")
            print(f"   Created: {created}")
            print("-" * 80)

    def check_balances(self, wallet_seed):
        """Check wallet balances"""
        wallet = mod1.get_account(wallet_seed)
        print(f"\n💼 Wallet: {wallet.address}")
        
        # Get XRP balance
        account_info = mod1.get_account_info(wallet.address)
        xrp_balance = int(account_info['Balance']) / 1000000  # Convert drops to XRP
        print(f"   XRP Balance: {xrp_balance} XRP")
        
        # Get token balances
        balance_info = mod2.get_balance(wallet_seed, wallet_seed)
        if 'balances' in balance_info:
            print("   Token Balances:")
            for currency, amount in balance_info['balances'].items():
                print(f"     {currency}: {amount}")

    def release_escrow(self, investment_id, admin_seed):
        """Admin: Release escrow for an investment (after finish_after time)"""
        data = self.load_data()
        investment = next((i for i in data['investments'] if i['id'] == investment_id), None)
        if not investment:
            print("❌ Investment not found")
            return
        owner = investment['escrow_owner']
        sequence = investment['escrow_sequence']
        print(f"   Releasing escrow for investment {investment_id} ...")
        result = finish_escrow(admin_seed, owner, sequence)
        print(result)

    def cancel_escrow(self, investment_id, admin_seed):
        """Admin: Cancel escrow for an investment (refund)"""
        data = self.load_data()
        investment = next((i for i in data['investments'] if i['id'] == investment_id), None)
        if not investment:
            print("❌ Investment not found")
            return
        owner = investment['escrow_owner']
        sequence = investment['escrow_sequence']
        print(f"   Cancelling escrow for investment {investment_id} ...")
        result = cancel_escrow(admin_seed, owner, sequence)
        print(result)