from pymongo import MongoClient
import os 
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set in environment")


# connect to MongoDB

client = MongoClient(MONGO_URI)

try: 
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect to MongoDB:", e)
db = client["ebay_price_tracker"]

