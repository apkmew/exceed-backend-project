from fastapi import FastAPI, HTTPException, Body
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
from math import ceil
from fastapi.middleware.cors import CORSMiddleware
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
    id : int
    stdID : str
    pay : int

class Deposit(BaseModel):
    id : int
    duration: int
    stdID: str
    items: list

client = MongoClient(f"mongodb://{user}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")
db = client['exceed04']
collection = db['lockers']

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/lockers")
def root():
    z = []
    for x in collection.find({},{"_id":0,"id" : 1 ,"available" : 1 ,"end_time": 1  }):
        # print(x)
        if x["available"] == True :
            x.pop("end_time")
        z.append(x)
    return z

@app.put("/deposit")
def deposit(dep: Deposit):
    locker = dep.dict()
    # print(dep)
    # print(locker)
    find = collection.find_one({"id": locker['id']})
    # print(find)
    now = datetime.now()
    # print(now.strftime("%d-%m-%Y %H:%M:%S"))
    nowToStr = now.strftime("%d-%m-%Y %H:%M:%S")
    end = now + timedelta(hours=locker['duration'])
    endToStr = end.strftime("%d-%m-%Y %H:%M:%S")
    # print(end)
    # test2 = datetime.strptime(strDate, "%d-%m-%Y %H:%M:%S")
    if(find['available']==True and len(locker['items'])!=0 and Locker['duration']>0 and 1 <= Locker['id'] <= 6):
        collection.update_one({"id": locker['id']}, {"$set": {
            "available" : False,
            "stdID" : locker['stdID'],
            "start_time" : nowToStr,
            "end_time" : endToStr,
            "duration" : locker['duration'],
            "items" : locker['items']
        }})
        return "Deposit completed"
    else:
        raise HTTPException(400, "Locker is unavailable or there is no items")

@app.put("/withdraw")
def withdraw(fwd: forWithdraw):
    lid = fwd.id
    stdID = fwd.stdID
    pay = fwd.pay
    data = collection.find_one({"id": lid}, {"stdID": stdID})
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