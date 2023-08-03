from config import MONGO_DETAILS
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.coin_bot
