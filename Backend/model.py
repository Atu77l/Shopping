from pydantic import BaseModel,Field
from typing import List

class UserCredentials(BaseModel):
    username: str
    password: str

# "full_name": name, "email": email,"username":username,"date_of_birth": dob, "password": password, "address": address
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    date_of_birth: str
    address:str
    username:str


class Leg(BaseModel):
    variation: int
    quantity: int
    optionType: str
    type: str
    expiry:str
    script:str
    stoplossQuantity: List[int] = Field(None)  # Corrected data type to List[int]
    stoploss: List[int]  = Field(None) # Corrected data type to List[float]
    target: List[int]  = Field(None)# Corrected data type to List[float]
    targetQuantity: List[int]  = Field(None) # Corrected data type to List[int]

class Strategy(BaseModel):
    clientId: str
    endTime: str
    expiry: str
    intraday: bool  # Corrected data type to bool
    placed: bool  # Corrected data type to bool
    scripts: str
    startTime: str
    strategyId: str
    strategyLevelStoploss: str
    strategyLevelTarget: str
    legs: List[Leg]

class Signal(BaseModel):
    _id: str
    serialno: str
    scriptname: str
    strikeprice: str
    expiry: str
    call_put: str
    strategyid: str
    buy_sell: str
    clientid: str
    date: str
    time: str
    exchange: str

class password(BaseModel):
    password:str
     

class Profile(BaseModel):
    full_name: str
    secret_key: str
    api_key: str
    broker_name: str
    email: str
    dob: str
    totp: str
    acc_password:str
    clientId:str
    

class strategyData(BaseModel):
    strategyName:str
    clientId: str
    endTime: str
    expiry: str
    intraday: bool  # Corrected data type to bool
    placed: bool  # Corrected data type to bool
    scripts: str
    startTime: str
    strategyId: str
    strategyLevelStoploss: str
    strategyLevelTarget: str
    legs: List[Leg]

class Roles(BaseModel):
    _id:str
    name:str

class Instrument(BaseModel):
    _id:str
    script:str
    g:int
    symbol:str

class forget(BaseModel):
    username:str
    email:str

class emailformat(BaseModel):
    username:str
    email:str
    
class resetDetail(BaseModel):
    email:str
    password:str
    token:str