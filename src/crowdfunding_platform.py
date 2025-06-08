import json
import os
from datetime import datetime
import mods.escrow_utils
from mods.nft_utils import prepare_nft_mint_tx
from mods.wallet import get_account_info, get_iou_balances, send_xrp
from mods.tokens import get_trustlines

class CrowdfundingPlatform:
    def __init__(self):
        self.storage_file = 'storage.json'
        self.init_storage()
        
    def init_storage(self):
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
        with open(self.storage_file, 'r') as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_campaign(self, farmer_name, project_title, description, funding_goal, farmer_address):
        print(f"\n🚜 Creating campaign for {farmer_name}...")
        data = self.load_data()
        campaign = {
            'id': data['next_campaign_id'],
            'farmer_name': farmer_name,
            'project_title': project_title,
            'description': description,
            'funding_goal': funding_goal,
            'farmer_address': farmer_address,
            'token_currency': None,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        data['campaigns'].append(campaign)
        data['next_campaign_id'] += 1
        self.save_data(data)
        print(f"✅ Campaign created with ID: {campaign['id']}")
        print(f"   Farmer address: {farmer_address}")
        return campaign['id']

    def approve_campaign(self, campaign_id):
        data = self.load_data()
        campaign = next((c for c in data['campaigns'] if c['id'] == campaign_id), None)
        if not campaign:
            print("❌ Campaign not found")
            return

        token_currency = campaign['project_title'][:3].upper()
        campaign['token_currency'] = token_currency
        campaign['status'] = 'approved'
        self.save_data(data)

        print(f"\n🎯 Campaign '{campaign['project_title']}' approved (pending on-chain setup).")
        print(f"   Token currency: {token_currency}")
        print("   Farmer must now configure their account for token issuance via their wallet (e.g., enable Default Ripple).")
        print("   Provide these instructions or a QR code to sign with a wallet app.")

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
        
        investor_wallet = get_account_info(investor_seed)
        
        print(f"\n💰 Processing investment of {investment_amount} XRP...")
        
        # Step 1: Send XRP to farmer
        print("   Sending XRP to farmer...")
        xrp_result = send_xrp(investor_seed, investment_amount, farmer_address)
        
        if "Submit failed" in str(xrp_result):
            print(f"❌ XRP transfer failed: {xrp_result}")
            return
            
        # Step 2: Create trust line for investor to receive tokens
        print("   Creating trust line for tokens...")
        trust_result = tokens.create_trust_line(investor_seed, farmer_address, token_currency, investment_amount * 10)
        
        # Step 3: Send project tokens to investor
        print("   Sending project tokens...")
        token_amount = investment_amount  # 1:1 ratio for MVP
        token_result = tokens.send_currency(farmer_seed, investor_wallet.address, token_currency, token_amount)
        
        # Record investment
        investment = {
            'id': data['next_investment_id'],
            'campaign_id': campaign_id,
            'investor_address': investor_wallet.address,
            'amount': investment_amount,
            'token_id': None,
            'created_at': datetime.now().isoformat()
        }
        
        data['investments'].append(investment)
        data['next_investment_id'] += 1
        self.save_data(data)
        
        print(f"✅ Investment successful!")
        print(f"   Received {token_amount} {token_currency} tokens")

    def provide_escrow_finish_instructions(self, investment_id, finisher_address):
        data = self.load_data()
        investment = next((i for i in data['investments'] if i['id'] == investment_id), None)
        if not investment:
            print("❌ Investment not found")
            return
        owner = investment['escrow_owner']
        sequence = investment['escrow_sequence']
        print(f"\nTo release escrow for investment {investment_id}, sign and submit this EscrowFinish transaction:")
        unsigned_finish_tx = prepare_escrow_finish_tx(
            account_address=finisher_address,  # Farmer's or admin's XRPL address
            owner=owner,
            sequence=sequence
        )
        print(json.dumps(unsigned_finish_tx, indent=2))
        print("Sign and submit this transaction with your XRPL wallet.")

    def provide_escrow_cancel_instructions(self, investment_id, canceller_address):
        data = self.load_data()
        investment = next((i for i in data['investments'] if i['id'] == investment_id), None)
        if not investment:
            print("❌ Investment not found")
            return
        owner = investment['escrow_owner']
        sequence = investment['escrow_sequence']
        print(f"\nTo cancel escrow for investment {investment_id}, sign and submit this EscrowCancel transaction:")
        unsigned_cancel_tx = prepare_escrow_cancel_tx(
            account_address=canceller_address,  # Usually investor's XRPL address
            owner=owner,
            sequence=sequence
        )
        print(json.dumps(unsigned_cancel_tx, indent=2))
        print("Sign and submit this transaction with your XRPL wallet.")

    def list_campaigns(self):
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

    def create_microloan(self, farmer_address, investor_seed, loan_amount, repayment_days):
        """Create an escrow-based microloan with full on-chain balance checks."""
        print(f"\n🏦 Creating microloan of {loan_amount} XRP...")

        # 1. Check if investor wallet exists and is funded
        investor_wallet = wallet.get_account(investor_seed)
        investor_info = get_account_info(investor_wallet.address)
        if not investor_info:
            print(f"❌ Investor wallet {investor_wallet.address} not found or not funded.")
            return None

        # 2. Check sufficient balance (add 2 XRP reserve)
        xrp_balance = int(investor_info['Balance']) / 1_000_000
        print(f"   Investor XRP balance: {xrp_balance} XRP")
        if xrp_balance < loan_amount + 2:
            print(f"❌ Insufficient funds. Need at least {loan_amount + 2} XRP.")
            return None

        # 3. Convert to drops and set escrow times
        loan_amount_drops = str(int(loan_amount * 1_000_000))
        repayment_seconds = int(repayment_days * 24 * 60 * 60)
        cancel_seconds = repayment_seconds + (7 * 24 * 60 * 60)  # 7-day grace

        # 4. Create time-based escrow
        print("   Creating escrow contract...")
        escrow_result = escrow_utils.create_time_escrow(
            investor_seed,
            loan_amount_drops,
            farmer_address,
            repayment_seconds,
            cancel_seconds
        )

        if isinstance(escrow_result, str) and "Submit failed" in escrow_result:
            print(f"❌ Escrow creation failed: {escrow_result}")
            return None

        # 5. Store microloan details
        data = self.load_data()
        if 'microloans' not in data:
            data['microloans'] = []
            data['next_microloan_id'] = 1

        microloan = {
            'id': data['next_microloan_id'],
            'farmer_address': farmer_address,
            'investor_address': investor_wallet.address,
            'loan_amount': loan_amount,
            'repayment_days': repayment_days,
            'status': 'active',
            'escrow_sequence': escrow_result.get('Sequence', 0),
            'created_at': datetime.now().isoformat()
        }
        data['microloans'].append(microloan)
        data['next_microloan_id'] += 1
        self.save_data(data)
        print(f"✅ Microloan created!")
        print(f"   Loan ID: {microloan['id']}")
        print(f"   Amount: {loan_amount} XRP")
        print(f"   Repayment due: {repayment_days} days")
        print(f"   Escrow sequence: {microloan['escrow_sequence']}")
        return microloan['id']

    def finish_microloan(self, microloan_id, farmer_seed):
        """Finish microloan escrow (farmer claims funds)."""
        data = self.load_data()
        microloan = next((ml for ml in data.get('microloans', []) if ml['id'] == microloan_id and ml['status'] == 'active'), None)
        if not microloan:
            print("❌ Microloan not found or already completed.")
            return

        print(f"\n💰 Finishing microloan #{microloan_id}...")
        finish_result = escrow_utils.finish_time_escrow(
            farmer_seed,
            microloan['investor_address'],
            microloan['escrow_sequence']
        )
        if isinstance(finish_result, str) and "Submit failed" in finish_result:
            print(f"❌ Escrow finish failed: {finish_result}")
            return

        microloan['status'] = 'completed'
        microloan['completed_at'] = datetime.now().isoformat()
        self.save_data(data)
        print(f"✅ Microloan completed! Farmer received {microloan['loan_amount']} XRP")

    def cancel_microloan(self, microloan_id, investor_seed):
        """Cancel microloan escrow (investor reclaims funds)."""
        data = self.load_data()
        microloan = next((ml for ml in data.get('microloans', []) if ml['id'] == microloan_id and ml['status'] == 'active'), None)
        if not microloan:
            print("❌ Microloan not found or already completed.")
            return

        print(f"\n🔄 Canceling microloan #{microloan_id}...")
        cancel_result = escrow_utils.cancel_escrow(
            investor_seed,
            microloan['investor_address'],
            microloan['escrow_sequence']
        )
        if isinstance(cancel_result, str) and "Submit failed" in cancel_result:
            print(f"❌ Escrow cancel failed: {cancel_result}")
            return

        microloan['status'] = 'cancelled'
        microloan['cancelled_at'] = datetime.now().isoformat()
        self.save_data(data)
        print(f"✅ Microloan cancelled! Investor reclaimed {microloan['loan_amount']} XRP")

    def check_balances(self, wallet_address):
        print(f"\n💼 Wallet: {wallet_address}")
        account_info = get_account_info(wallet_address)
        if not account_info:
            print("   This account does not exist or is not yet funded on the XRPL ledger.")
            return
        xrp_balance = int(account_info['Balance']) / 1000000
        print(f"   XRP Balance: {xrp_balance} XRP")
        token_balances = get_iou_balances(wallet_address)
        print("   Token Balances:")
        for iou in token_balances:
            print(f"     {iou['currency']} (issuer: {iou['account']}): {iou['balance']}")

    def display_trustlines(self, wallet_address):
        print(f"\n🔗 Trustlines for {wallet_address}:")
        trustlines = get_trustlines(wallet_address)
        if not trustlines:
            print("   No trustlines found.")
            return
        for tl in trustlines:
            print(f"   {tl['currency']} issued by {tl['account']}: "
                  f"Limit {tl['limit']}, Balance {tl['balance']}")