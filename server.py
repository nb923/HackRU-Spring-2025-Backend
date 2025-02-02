from fastapi import FastAPI, HTTPException
import random

from pydantic import BaseModel

app = FastAPI()

SHOPPING_DB = {
    "Green Apple": [1.0, 20, 15, 6, 0.3],
    "banana": [0.5, 5, 35, 2, 0.2],
    "orange": [0.8, 7, 25, 19, 0.1],
    "milk": [2.5, 150, 8, 0, 8.0],
    "bread": [3.0, 80, 3, 45, 1.5]
}

shopping_log = {
    12345: [
        [True, "Laptop", [1.0, 20, 15, 6, 0.3], None],
        [False, "Invalid item", None, None],
        [False, "Checkout", None, True]
    ],
    12346: [
        [True, "Phone", [1.0, 20, 15, 6, 0.3], None],
        [False, "Invalid item", None, None],
        [False, "Checkout", None, True]
    ]
}

@app.get("/get-new-shopping-id/")
async def get_new_shopping_id():
    new_shopping_id = random.randint(10000, 99999)
    
    while new_shopping_id in shopping_log:
        new_shopping_id = random.randint(10000, 99999)

    shopping_log[new_shopping_id] = []
    
    return {"new_shopping_id": new_shopping_id}

@app.get("/get-shopping-log/{shopping_id}")
async def get_shopping_log(shopping_id: int):
    if shopping_id not in shopping_log:
        raise HTTPException(status_code=404, detail="Shopping ID not found")
    
    return {"shopping_id": shopping_id, "log": shopping_log[shopping_id]}

class ItemRequest(BaseModel):
    item_name: str
    shopping_id: int

@app.post("/detect-item/")
async def detect_item(item_request: ItemRequest):
    item_name = item_request.item_name.lower()
    shopping_id = item_request.shopping_id

    if shopping_id not in shopping_log:
        raise HTTPException(status_code=404, detail="Shopping ID not found")

    if item_name in SHOPPING_DB:
        item_data = SHOPPING_DB[item_name]
        item_price, calories, protein, carbs, fat = item_data

        shopping_log[shopping_id].append([True, item_name.capitalize(), item_data, None])
        return {"message": f"Item '{item_name.capitalize()}' added to the shopping log."}
    else:
        shopping_log[shopping_id].append([False, "Invalid item", None, None])
        return {"message": "Invalid item. Not found in the shopping database."}


