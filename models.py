from pydantic import BaseModel, Field
from enum import Enum

NETWORK_PLATFORM_ID = {
    'ETH':1,
    'BSC':14
}

class Network(str, Enum):
    ETH = "ethereum"
    BSC = "bsc"
    
class TokenModel(BaseModel):
    base_token_name: str = Field(...)
    base_token_address: str = Field(...)
    quote_token_name: str = Field(...)
    quote_token_address: str = Field(...)
    network: str = Field(...)
    market_cap: int = Field(...)

    class Config:

        json_schema_extra = {
            "example": {
                "base_token_name": "CoCo",
                "base_token_address": "0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "quote_token_name": "CoCo",
                "quote_token_address":"0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "network": "ethereum",
                "market_cap": 563352341
            }
        }
        
def token_helper(token) -> dict:
    return {
        "id": str(token["_id"]),
        "base_token_name": token["base_token_name"],
        "base_token_address": token["base_token_address"],
        "quote_token_name": token["quote_token_name"],
        "quote_token_address": token["quote_token_address"],
        "network": token['network'],
        "market_cap": token['market_cap'],
    }
        
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}