from fastapi import FastAPI, HTTPException, Body
from datetime import date, datetime, timedelta
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
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

class Deposit(BaseModel):
    id : int
    duration: int
    stdID: str
    items: list

client = MongoClient(f"mongodb://{user}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")
db = client['exceed04']
collection = db['lockers']

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

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
    if(find['available']==True and len(locker['items'])!=0):
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
