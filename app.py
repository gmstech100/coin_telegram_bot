import uvicorn

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from database import database
from process import insert_token, get_tokens
from models import TokenModel, ResponseModel, token_helper
from process import processing_coin_info


app = FastAPI()

@app.post("/add_token", response_description="Add new token")
async def add_token(token_name:str, token_url:str):
    base_token_address, base_token_pool_id = processing_coin_info(token_url)
    token_dict = {
        "name": token_name,
        "token": base_token_address,
        "pool_id": str(base_token_pool_id),
    }
    token = TokenModel(**token_dict)
    token = jsonable_encoder(token)
    new_token = await database["tokens"].insert_one(token)
    return ResponseModel(data=token_dict,message="Insert successfully")

@app.get("/get_tokens", response_description="Get list tokens")
async def get_tokens():
    list_tokens_db = await database['tokens'].find().to_list(50)
    tokens = [token_helper(token) for token in list_tokens_db]
    return ResponseModel(data=tokens,message="Get list tokens successfully")
    

if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8888)