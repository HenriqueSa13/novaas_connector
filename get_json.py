import json
import pandas as pd


f = open('http___smart_festo_com_id_instance_aas_5140_0142_3091_4340.aas.json')
#open aasx model file (json)
data = json.load(f)

evt_list = list()
n_properties = 0

#check aas id
aas_id = data["assetAdministrationShells"][0]["identification"]["id"]
print(aas_id)

for i in range(0,len(data["submodels"])) :
    if data["submodels"][i]["idShort"] == "OperationalData":
        aas_opdata = data["submodels"][i]["submodelElements"]

for i in range(0,len(aas_opdata)) :
    if aas_opdata[i]["modelType"]["name"] == "Property":
        n_properties += 1

    if aas_opdata[i]["modelType"]["name"] == "BasicEvent":
        evt_list.append(aas_opdata[i])



#print(len(aas_opdata))
   
f.close()