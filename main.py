from fastapi import FastAPI, HTTPException, Body
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
from math import ceil
import os
load_dotenv('.env')

user = os.getenv('user')
password = os.getenv('password')

class Locker(BaseModel):
    id : int
    available : bool
    stdID : str
    start_time : datetime
    end_time : datetime
    duration : int
    items : list

class forWithdraw(BaseModel):
    stdID : str
    pay : int

client = MongoClient(f"mongodb://{user}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")
db = client['exceed04']
collection = db['lockers']

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/withdraw")
def withdraw(fwd: forWithdraw):
    stdID = fwd.stdID
    pay = fwd.pay
    data = collection.find_one({"stdID": stdID})
    if data is None:
        raise HTTPException(status_code=404, detail="Student ID not found")
    localTime = datetime.now()
    end_time = datetime.strptime(data['end_time'], "%d-%m-%Y %H:%M:%S")
    duration = data['duration']
    fee = 0
    if duration > 2 : fee += 5*(duration-2)
    if localTime > end_time:
        diff = localTime - end_time
        minutes = ceil(diff.total_seconds()/60)
        fee += ceil(minutes/10)*20
    if pay < fee:
        raise HTTPException(status_code=400, detail=f"Not enough money to withdraw. Need {fee} baht")
    collection.update_one(data, {"$set":{"available": True, "stdID": "", "start_time": "", "end_time": "", "duration": 0, "items": []}})
    return {"pay": pay, "fee": fee, "change": pay-fee}