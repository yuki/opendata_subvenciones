from fastapi import FastAPI
import pymongo

# formamos la URI de conexión al servidor local
uri_mongo = "mongodb://root:example@127.0.0.1/?retryWrites=true&w=majority"

# Conectar al servicio MongoDB
con_local = pymongo.MongoClient(uri_mongo)
mongodb = con_local["subvenciones"]
mongocol = mongodb.get_collection("granted_benefits")



app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}

@app.get("/granted-benefits")
async def get_granted_benefits():
    x = mongocol.find({},{'_id': 0})[0]
    return x

@app.get("/granted-benefits/{beneficiaryId}")
async def get_granted_benefits_by_beneficiary(beneficiaryId: str):
    return {"XX"}
