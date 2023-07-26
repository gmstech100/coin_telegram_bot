import motor.motor_asyncio
import uvicorn

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from apis import MONGO_DETAILS
from models import TokenModel


app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.college

@app.post("/", response_description="Add new token", response_model=TokenModel)
async def create_student(token: TokenModel = Body(...)):
    token = jsonable_encoder(token)
    new_token = await db["coin_bot"].insert_one(token)
    created_token = await db["coin_bot"].find_one({"_id": new_token.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_token)


if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=8888)