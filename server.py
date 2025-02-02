from fastapi import FastAPI, HTTPException
import random
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Get the MongoDB connection string from the environment variable
connection_string = os.getenv('MONGODB_URL')

client = MongoClient(connection_string)

# Select the database (this will create the database if it doesn't exist)
db = client['shopping_db']  # Name of your database

# Select the shopping_logs collection
logs_collection = db['shopping_logs']  # Collection for shopping logs
nutrition_collection = db['product_nutrition']

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

@app.get("/get-shopping-log/{shopping_id}")
async def get_shopping_log(shopping_id: int):
    if shopping_id not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
        raise HTTPException(status_code=404, detail="Shopping ID not found")
    
    log = get_shopping_log(shopping_id)
    
    return log

class ItemRequest(BaseModel):
    item_name: str
    shopping_id: int

@app.post("/detect-item/")
async def detect_item(item_request: ItemRequest):
    item_name = item_request.item_name.lower()
    shopping_id = item_request.shopping_id

    if shopping_id not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
        raise HTTPException(status_code=404, detail="Shopping ID not found")
    
    item = nutrition_collection.find_one({"product_name": {"$regex": item_name, "$options": 'i'}})

    if item:
        log_entry = {
            "id": shopping_id,
            "product_name": item["product_name"],
            "calories": item["calories"],
            "carbs": item["carbs"],
            "fat": item["fat"],
            "protein": item["protein"],
            "price": item["price"]
        }

        logs_collection.update_one(
            {"user_id": shopping_id},
            {"$push": {"log": log_entry}}
        )

        return {"message": f"Item '{item_name.capitalize()}' added to the shopping log."}
    else:
        return {"message": "Invalid item. Not found in the shopping database."}
    
# Checkout Request Body
class CheckoutRequest(BaseModel):
    shopping_id: int
    
@app.post("/checkout")
async def checkout(request: CheckoutRequest):
    shopping_id = request.shopping_id

    if shopping_id not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
        raise HTTPException(status_code=404, detail="Shopping ID not found")

    # Find the user's shopping log
    user_log = logs_collection.find_one({"user_id": shopping_id})

    if not user_log:
        raise HTTPException(status_code=404, detail="Shopping log not found")

    # Clear the user's shopping log
    logs_collection.update_one(
        {"user_id": shopping_id},
        {"$set": {"log": []}}  # Set the log to an empty list, effectively clearing it
    )
    
    return {"message": f"Checkout successful, cart {shopping_id} is now empty."}
    
def get_shopping_log(user_id):
    # Find the document for the given user_id
    shopping_log_entry = logs_collection.find_one({"user_id": user_id})

    if shopping_log_entry:
        return shopping_log_entry['log']  # Return the log data
    else:
        return f"Shopping log for user_id {user_id} not found."


