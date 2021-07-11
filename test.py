

import json

users = None
balance = 500
with open("main-bank.json", "r") as f:
    data = json.load(f)
    users = data["users"]

user_id = 1234
existing_users = data["users"]

for user in existing_users:
    if user["id"] == user_id:
        is_in = existing_users[str(user_id)]["wallet"], existing_users[str(user_id)]["bank"]

data["users"] += [{"id": str(user_id),
        "wallet": balance, 
        "bank": balance}]

with open("main-bank.json", "r+") as f:
    json.dump(data, f)
    

