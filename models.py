from pydantic import BaseModel, Field
from enum import Enum

NETWORK_PLATFORM_ID = {
    'ethereum':1,
    'bsc':14
}

class Network(str, Enum):
    ETH = "ethereum"
    BSC = "bsc"
    
class TokenModel(BaseModel):
    base_token_name: str = Field(...)
    base_token_address: str = Field(...)
    quote_token_name: str = Field(...)
    quote_token_address: str = Field(...)
    pair_address: str = Field(...)
    network: str = Field(...)
    market_cap: int = Field(...)
    pool_id: str=Field(...)
    description: str = Field(...)
    token_telegram: str = Field(...)
    chart: str = Field(...)
    trade: str = Field(...)
    snipe: str = Field(...)
    trending: str = Field(...)
    ads_text: str = Field(...)
    ads_url: str = Field(...)

    class Config:

        json_schema_extra = {
            "example": {
                "base_token_name": "CoCo",
                "base_token_address": "0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "quote_token_name": "CoCo",
                "quote_token_address":"0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "pair_address":"0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "network": "ethereum",
                "market_cap": 563352341,
                "pool_id": "563352341",
                "description":'description',
                "token_telegram":"token_telegram",
                "chart":"chart",
                "snipe":"snipe",
                "trade":"trade",
                "trending":"trending",
                "ads_text": "AAAAAAAAAAA",
                "ads_url": "https://t.me/kir_inu"
            }
        }
        
def token_helper(token) -> dict:
    return {
        "id": str(token["_id"]),
        "base_token_name": token["base_token_name"],
        "base_token_address": token["base_token_address"],
        "quote_token_name": token["quote_token_name"],
        "quote_token_address": token["quote_token_address"],
        "pair_address": token["pair_address"],
        "network": token['network'],
        "market_cap": token['market_cap'],
        "pool_id": token['pool_id'],
        "description": token['description'],
        "token_telegram":token['token_telegram'],
        "chart":token['chart'],
        "snipe":token['snipe'],
        "trade":token['trade'],
        "trending":token['trending'],
        "ads_text":token['ads_text'],
        "ads_url":token['ads_url']
    }
        
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}