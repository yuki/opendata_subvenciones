#!/usr/bin/env python3

import requests as re
import json
import pymongo

# formamos la URI de conexión al servidor local
uri_mongo = "mongodb://root:example@127.0.0.1/?retryWrites=true&w=majority"

# Conectar al servicio MongoDB
con_local = pymongo.MongoClient(uri_mongo)
mongodb = con_local["subvenciones"]



def organizationGroups():
    url = "https://api.euskadi.eus/granted-benefit/v1.0/organizationGroups"
    datos = re.get(url).json()
    mongodb.organizationGroups.insert_many(datos["organizationGroups"])


def subvenciones():
    page = 1
    elements = 500
    descargar = True
    while descargar:
        url = "https://api.euskadi.eus/granted-benefit/v1.0/granted-benefits?_elements="+str(elements)+"&_page="+str(page)
        datos = re.get(url).json()
        mongodb.granted_benefits.insert_many(datos["granted-benefits"])
        print("Descargada página subvenciones: " + str(page))
        page = page + 1
        if page > datos["totalPages"]:
            descargar = False


def main():
    print("Inicio")
    organizationGroups()
    subvenciones()
    print("Fin")





if __name__ == "__main__":
    main()