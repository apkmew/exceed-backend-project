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

client = MongoClient(f"mongodb://{user}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")
db = client['exceed04']
collection = db['lockers']

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}