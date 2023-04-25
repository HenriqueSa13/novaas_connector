import json

f = open('http___smart_festo_com_id_instance_aas_5140_0142_3091_4340.aas.json')
#open aasx model file (json)
data = json.load(f)

evt_list = list()
n_properties = 0
n_properties_in_flow = 0

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

#print(json.dumps(evt_list,indent=2))
#print(len(aas_opdata))
   
f.close()

with open('flow_opdata_todo.json', 'r') as f_flow:

    flow_data = json.load(f_flow)

    
    
    for i in range(0,len(flow_data)):   
        if "name" in flow_data[i].keys():
            if flow_data[i]["name"] == "Property handler":
                propertyhandler_id = flow_data[i]["id"]
                print(flow_data[i]["id"])
                break
    j=0
    for i in range(0,len(flow_data)):
        
        if "type" in flow_data[i].keys():

            if flow_data[i]["type"] == ("subflow:" + propertyhandler_id) and ("Property " in flow_data[i]["name"]):
                n_properties_in_flow += 1
                
                if len(flow_data[i]["env"]) > 2:
                    continue
                
                propertylink_dict = {}
                propertylink_dict["name"] = "PropertyLink"
                propertylink_dict["type"] = "str"
                propertylink_dict["value"] = aas_id + "/OperationalData/" + evt_list[j]["observed"]["keys"][2]["value"]
                
                propertylinkevt_dict = {}
                propertylinkevt_dict["name"] = "PropertyLinkEvt"
                propertylinkevt_dict["type"] = "str"
                propertylinkevt_dict["value"] = aas_id + "/OperationalData/" + evt_list[j]["idShort"]
                
                flow_data[i]["env"].insert(1,propertylink_dict)
                flow_data[i]["env"].insert(3,propertylinkevt_dict)
                
                j += 1
                
    """
    prop submodel = flow - ok
    prop submodel > flow - sao todas preenchidas no flow mas ficam em falta (possivel adicionar nos extra depois)
    prop submodel < flow - erro (evt list nao tem elementos suficientes - break do ciclo quando acabam elementos na lista?)
    """
    if n_properties != n_properties_in_flow:
        print("WARNING")
        print("Number of properties mismatch: \n properties in submodel - " + str(n_properties) + "\n properties in flow - " + str(n_properties_in_flow))
        #exit() 


with open('flow_opdata_todo.json', 'w') as f_flow:
    json.dump(flow_data, f_flow)

