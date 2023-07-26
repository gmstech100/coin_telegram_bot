import uvicorn

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from process import insert_token, get_tokens
from models import TokenModel, ResponseModel
from process import processing_coin_info


app = FastAPI()

@app.post("/add_token", response_description="Add new token")
async def add_token(token_name:str, token_url:str):
    base_token_address, base_token_pool_id = await processing_coin_info(token_url)
    token_dict = {
        "name": token_name,
        "token": base_token_address,
        "pool_id": str(base_token_pool_id),
    }
    token = TokenModel(**token_dict)
    token = jsonable_encoder(token)
    new_token = insert_token(token)
    return ResponseModel(data=new_token,message="Insert successfully")

@app.get("/get_tokens", response_description="Get list tokens")
async def get_tokens():
    return ResponseModel(data=get_tokens(),message="Get list tokens successfully")
    


if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8888)