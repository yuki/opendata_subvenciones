#!/usr/bin/env python3

import uvicorn

from pydantic import BaseModel

from bson import SON
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import  Page, add_pagination, Params as BaseParams
from fastapi_pagination.ext.motor import paginate
from fastapi_pagination.links.default import Page

#############################################
#
# Needed variables
#
#############################################
# MongoDB URI style: mongodb://user:password@host:port
uri_mongo = "mongodb://root:example@127.0.0.1:27017"
app = FastAPI()

## CORS should be disabled
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client: AsyncIOMotorClient


#############################################
#
# Fastapi_pagination's params changes
#
#############################################
from typing import TypeVar, Generic
T = TypeVar("T")

class Params(BaseParams):
    # to change limits
    size: int = Query(100, ge=1, le=1000, description="Page size")

class Page(Page[T], Generic[T]):
    __params_type__ = Params


#############################################
#
# Documents to Objects 
#
#############################################
class Beneficiary(BaseModel):
    id:   str
    name: str

class Granted(BaseModel):
    date: str # MUST BE CHANGED
    amount: float

class GrantedBenefit(BaseModel):
    _id: int
    oid: str
    benefitId: str
    # nameByLang: str
    beneficiary: Beneficiary
    granted: Granted
    importPackageOid: str
    class Config:
        orm_mode = True


#############################################
#
# API's endpoints
#
#############################################
@app.on_event("startup")
async def on_startup() -> None:
    global client
    client = AsyncIOMotorClient(uri_mongo)


@app.get("/")
async def root():
    """
    Return: "Hello to the API"
    """
    return {"message": "Hello to the API"}


@app.get("/granted-benefits/ranking")
async def get_ranking():
    # MongoDB query:
    # db.granted_benefits.aggregate([{
    #     $group: { 
    #         _id: { nif: "$beneficiary.id" }, 
    #         totalAmount: { $sum:"$granted.amount"},
    #         count: { $sum: 1 }  
    #     }
    # }]).sort({totalAmount:-1})

    pipeline = [
        {"$group": {
                "_id": { "nif": "$beneficiary.id" },
                "totalAmount": { "$sum":"$granted.amount" },
                "count": { "$sum": 1 }
            }
        },
        {"$sort": SON([("count", -1)])},
        {"$limit": 50}
    ]
    x = client.subvenciones.granted_benefits.aggregate(pipeline)
    return await x.to_list(length=None)


@app.get("/granted-benefits",response_model=Page[GrantedBenefit])
async def get_granted_benefits():
    return await paginate(client.subvenciones.granted_benefits)



@app.get("/granted-benefits/SearchBeneficiaryName/{beneficiaryName}")
async def get_granted_benefits_by_beneficiary(beneficiaryName: str):
    # MongoDB query: 
    #   db.granted_benefits.aggregate([
    #       {$match:{"beneficiary.name":{$regex:"XXX","$options":"i"}}}, 
    #       {$group: {"_id":"$beneficiary.id", "name":{ "$first": { "$toUpper": "$beneficiary.name"}  }}}
    #   ])
    pipeline = [
        {"$match": {"beneficiary.name":{"$regex":beneficiaryName,"$options":"i"}}},
        {"$group": {"_id":"$beneficiary.id", "name":{ "$first": { "$toUpper": "$beneficiary.name"}}}}
    ]
    x = client.subvenciones.granted_benefits.aggregate(pipeline)
    return await x.to_list(length=None)



@app.get("/granted-benefits/byBeneficiary/{beneficiaryId}",response_model=Page[GrantedBenefit])
async def get_granted_benefits_by_beneficiary(beneficiaryId: str):
    # MongoDB query: db.granted_benefits.find({"beneficiary.id":"beneficiaryId"})
    return await paginate(client.subvenciones.granted_benefits,{"beneficiary.id": beneficiaryId})


# Add pagination to the API
add_pagination(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
