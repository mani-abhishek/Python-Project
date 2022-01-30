from typing import Optional
from fastapi import FastAPI

from pydantic import BaseModel
APP = FastAPI()
def get_standard(age, level):
    standard = age- 6
    # level = level.lower()
    if str(level).lower() == 'basic':
            standard-=1
            return standard
    elif str(level).lower() == 'intermediate':
            return standard
    elif str(level).lower() == 'advanced':
            standard+=1
            return standard

@APP.get('/')
async def hello_world():
    return {"Hello world !"}

@APP.get('/Standard/')
async def components(age: int, level : str):
    standard = get_standard(age, level)
    return {"Standard" : {standard}}





