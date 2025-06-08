from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from crowdfunding_platform import CrowdfundingPlatform

app = FastAPI()
platform = CrowdfundingPlatform()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CampaignCreateReq(BaseModel):
    farmer_name: str
    project_title: str
    description: str
    funding_goal: int

class InvestReq(BaseModel):
    campaign_id: int
    investor_seed: str
    amount: int

class MintNFTReq(BaseModel):
    seed: str
    uri: str

class BalanceReq(BaseModel):
    wallet_seed: str

@app.post("/campaigns")
def create_campaign(req: CampaignCreateReq):
    campaign_id = platform.create_campaign(
        req.farmer_name, req.project_title, req.description, req.funding_goal
    )
    return {"campaign_id": campaign_id}

@app.get("/campaigns")
def list_campaigns():
    data = platform.load_data()
    return {"campaigns": data.get("campaigns", [])}

@app.post("/invest")
def invest(req: InvestReq):
    platform.invest_in_campaign(req.campaign_id, req.investor_seed, req.amount)
    return {"success": True}

@app.post("/mint_nft")
def mint_nft(req: MintNFTReq):
    from nft_utils import mint_nft
    nft_id, tx_result = mint_nft(req.seed, req.uri)
    return {"nft_id": nft_id, "tx_result": tx_result}

@app.post("/balance")
def check_balance(req: BalanceReq):
    from wallet import get_account, get_account_info
    wallet = get_account(req.wallet_seed)
    info = get_account_info(wallet.address)
    xrp_balance = int(info["Balance"]) / 1_000_000
    return {"address": wallet.address, "xrp_balance": xrp_balance}
