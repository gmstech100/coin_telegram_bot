from pydantic import BaseModel, Field
    
class TokenModel(BaseModel):
    name: str = Field(...)
    token: str = Field(...)
    pool_id: str = Field(...)

    class Config:

        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "token": "0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "pool_id": "7461333",
            }
        }
        
def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}