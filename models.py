from bson import ObjectId
from pydantic import BaseModel, Field

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    # @classmethod
    # def __get_pydantic_json_schema__(cls, field_schema):
    #     field_schema.update(type="string")
        
        
class TokenModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    token: str = Field(...)
    pool_id: int = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "token": "0xa3c31927a092bd54eb9a0b5dfe01d9db5028bd4f",
                "pool_id": "7461333",
            }
        }