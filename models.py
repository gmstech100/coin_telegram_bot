from pydantic import BaseModel, Field
from enum import Enum

NETWORK_PLATFORM_ID = {
    'ETH':1,
    'BSC':14
}

class Network(str, Enum):
    ETH = "etherum"
    BSC = "bsc"
    
class TokenModel(BaseModel):
    name: str = Field(...)
    token: str = Field(...)
    pool_id: str = Field(...)
    network: str = Field(...)
    market_cap: int = Field(...)

    class Config:

        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "token": "0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "pool_id": "7461333",
                "network": "etherum",
                "market_cap": 563352341
            }
        }
        
def token_helper(token) -> dict:
    return {
        "id": str(token["_id"]),
        "name": token["name"],
        "token": token["token"],
        "pool_id": token["pool_id"],
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