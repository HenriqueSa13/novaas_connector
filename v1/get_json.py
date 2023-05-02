import json
import tkinter as tk
import tkinter.filedialog
import copy

history_length = "14400"

root = tk.Tk()
root.withdraw()
filepath_assetjson = tk.filedialog.askopenfilename(initialdir="./v1" ,title="Asset JSON file:")

f = open(filepath_assetjson)
#open aasx model file (json)
data = json.load(f)

coll_list = list()
evt_list = list()
main_list = list()
list_x = list()
level = 0
n_properties = 0
n_properties_in_flow = 0

#check aas id
aas_id = data["assetAdministrationShells"][0]["identification"]["id"]
print(aas_id)

for i in range(0,len(data["submodels"])) :
    if data["submodels"][i]["idShort"] == "OperationalData":
        aas_opdata = data["submodels"][i]["submodelElements"]
        break

for i in range(0,len(aas_opdata)) :
    if aas_opdata[i]["modelType"]["name"] == "SubmodelElementCollection":
        main_list.append(aas_opdata[i]["idShort"])
        coll_list.append(aas_opdata[i]["value"])

    if aas_opdata[i]["modelType"]["name"] == "Property":
        n_properties += 1

    if aas_opdata[i]["modelType"]["name"] == "BasicEvent":
        evt_list.append(aas_opdata[i]["idShort"])

#print(json.dumps(evt_list,indent=2))
#print(len(aas_opdata))

print(len(coll_list[0]))
print(main_list)

while len(coll_list) != 0:
    initial_len = len(coll_list)
    aux_list = copy.deepcopy(main_list)

    for i in range(0,len(coll_list)):
        for j in range(0,len(coll_list[i])):
            if coll_list[i][j]["modelType"]["name"] == "SubmodelElementCollection":
                coll_list.append(coll_list[i][j]["value"])
                if len(main_list) < j + 1:
                    main_list.insert(j,aux_list[i] + "." + coll_list[i][j]["idShort"])
                else:
                    main_list[j] = aux_list[i] + "." + coll_list[i][j]["idShort"]

            if coll_list[i][j]["modelType"]["name"] == "BasicEvent":
                evt_list.append(coll_list[i][j]["idShort"])
 
    del coll_list[:initial_len]
          
print(main_list)
print(evt_list)      

f.close()


#-------------------------------------------------------------------------

root = tk.Tk()
root.withdraw()
filepath_flow = tk.filedialog.askopenfilename(title="Node-Red flow JSON file:")

with open(filepath_flow, 'r') as f_flow:

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
                
                if len(flow_data[i]["env"]) > 0:
                    continue
    
                property_dict = {}
                property_dict["name"] = "PropertyName"
                property_dict["type"] = "str"
                property_dict["value"] = evt_list[j]["observed"]["keys"][2]["value"]
                
                propertylink_dict = {}
                propertylink_dict["name"] = "PropertyLink"
                propertylink_dict["type"] = "str"
                propertylink_dict["value"] = aas_id + "/OperationalData/" + evt_list[j]["observed"]["keys"][2]["value"]
                
                historylength_dict = {}
                historylength_dict["name"] = "HistoryLength"
                historylength_dict["type"] = "num"
                historylength_dict["value"] = history_length

                propertylinkevt_dict = {}
                propertylinkevt_dict["name"] = "PropertyLinkEvt"
                propertylinkevt_dict["type"] = "str"
                propertylinkevt_dict["value"] = aas_id + "/OperationalData/" + evt_list[j]["idShort"]
                
                flow_data[i]["env"].insert(0,property_dict)
                flow_data[i]["env"].insert(1,propertylink_dict)
                flow_data[i]["env"].insert(2,historylength_dict)
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


with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)


