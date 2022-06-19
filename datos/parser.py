#!/usr/bin/env python3

# Con este script se va a tratar de parsear todos los datos tras realizar la importación.
# ¿Por qué? El problema es que haciendo una primera búsqueda por nombres tras la importación
# se han encontrado con el "beneficiary.id" "*********" muchas empresas que no deberían tener
# ese id, porque son empresa que ya tienen su CIF. 
# ¿Cómo se puede ver eso? Haciendo la siguiente búsqueda a los datos importados:
# db.granted_benefits.aggregate([
#   {$match:{"beneficiary.name":{$regex:"XXX","$options":"i"}}}, 
#   {$group: {"_id":"$beneficiary.id", "name":{ "$first": { "$toUpper": "$beneficiary.name"}  }}}  
# ])
# También existen "beneficiary.id" con algunos números quitados.

import json
import pymongo
import re

# formamos la URI de conexión al servidor local
uri_mongo = "mongodb://root:example@127.0.0.1/?retryWrites=true&w=majority"
con_local = pymongo.MongoClient(uri_mongo)
collection = con_local["subvenciones"].granted_benefits


def main():
    print("Inicio")
    all = collection.find()
    new_data = {}
    for doc in all:
        if not doc["beneficiary"]["id"] in new_data:
            new_data[doc["beneficiary"]["id"]] = []
        if "name" in doc["beneficiary"].keys():
            name = re.sub(' +', ' ',doc["beneficiary"]["name"].lower())
            if not name in new_data[doc["beneficiary"]["id"]]:
                new_data[doc["beneficiary"]["id"]].append(name)
    f = open("cifs.txt", "a")
    for cif in new_data:
        f.write(cif + " " + str(new_data[cif])+"\n")
    f.close()
    print("Fin")


if __name__ == "__main__":
    main()