import json
import tkinter as tk
import tkinter.filedialog
import copy
import secrets

history_length = "14400"

root = tk.Tk()
root.withdraw()
filepath_assetjson = tk.filedialog.askopenfilename(initialdir="./v1" ,title="Asset JSON file:")

f = open(filepath_assetjson)
#open aasx model file (json)
data = json.load(f)

coll_list = list()
evt_list = list()
evt_name = ""
n_properties_w_event = 0
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
        coll_list.append(aas_opdata[i]["value"])

    if aas_opdata[i]["modelType"]["name"] == "BasicEvent":
        for j in range(2,len(aas_opdata[i]["observed"]["keys"])):
            if j == len(aas_opdata[i]["observed"]["keys"]) - 1:
                evt_name += aas_opdata[i]["observed"]["keys"][j]["value"] + "Evt"
            else:
                evt_name += aas_opdata[i]["observed"]["keys"][j]["value"] + "."
        
        n_properties_w_event +=1
        evt_list.append(evt_name) 
        evt_name = ""    

while len(coll_list) != 0:
    initial_len = len(coll_list)

    for i in range(0,len(coll_list)):
        for j in range(0,len(coll_list[i])):
            if coll_list[i][j]["modelType"]["name"] == "SubmodelElementCollection":
                coll_list.append(coll_list[i][j]["value"])

            if coll_list[i][j]["modelType"]["name"] == "BasicEvent":
                for k in range(2,len(coll_list[i][j]["observed"]["keys"])):
                    if k == len(coll_list[i][j]["observed"]["keys"])-1:
                        evt_name += coll_list[i][j]["observed"]["keys"][k]["value"] + "Evt"
                    else:
                        evt_name += coll_list[i][j]["observed"]["keys"][k]["value"] + "."
                
                n_properties_w_event +=1
                evt_list.append(evt_name) 
                evt_name = ""
 
    del coll_list[:initial_len]
          
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
                break
    j=0
    for i in range(0,len(flow_data)):
        
        if "type" in flow_data[i].keys():

            if flow_data[i]["type"] == ("subflow:" + propertyhandler_id) and ("Property " in flow_data[i]["name"]): #search for all the properties
                n_properties_in_flow += 1
                
                #dont overwrite if not first time - just for testing
                if ("env" in flow_data[i].keys()) and (len(flow_data[i]["env"]) > 0) :
                    continue

                #generate name, link, historylength and linkevt for env of property

                property_dict = {}
                property_dict["name"] = "PropertyName"
                property_dict["type"] = "str"
                property_dict["value"] = evt_list[j].replace("Evt","")
                
                propertylink_dict = {}
                propertylink_dict["name"] = "PropertyLink"
                propertylink_dict["type"] = "str"
                propertylink_dict["value"] = aas_id + "/OperationalData/" + evt_list[j].replace("Evt","")
                
                historylength_dict = {}
                historylength_dict["name"] = "HistoryLength"
                historylength_dict["type"] = "num"
                historylength_dict["value"] = history_length

                propertylinkevt_dict = {}
                propertylinkevt_dict["name"] = "PropertyLinkEvt"
                propertylinkevt_dict["type"] = "str"
                propertylinkevt_dict["value"] = aas_id + "/OperationalData/" + evt_list[j]
                
                flow_data[i].update({"env":[]})

                flow_data[i]["env"].insert(0,property_dict)
                flow_data[i]["env"].insert(1,propertylink_dict)
                flow_data[i]["env"].insert(2,historylength_dict)
                flow_data[i]["env"].insert(3,propertylinkevt_dict)

                #generate wires: 2, 1, 1
                flow_data[i]["wires"][0].append(secrets.token_hex(8))
                flow_data[i]["wires"][0].append(secrets.token_hex(8))
                flow_data[i]["wires"][1].append(secrets.token_hex(8))
                flow_data[i]["wires"][2].append(secrets.token_hex(8))
   
                j += 1
                
    """
    prop submodel = flow - ok
    prop submodel > flow - sao todas preenchidas no flow mas ficam em falta (possivel adicionar nos extra depois)
    prop submodel < flow - erro (evt list nao tem elementos suficientes - break do ciclo quando acabam elementos na lista?)
    """
    if n_properties_w_event != n_properties_in_flow:
        print("WARNING")
        print("Number of properties mismatch: \n properties in submodel - " + str(n_properties_w_event) + "\n properties in flow - " + str(n_properties_in_flow))
        #exit() 


with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)

with open(filepath_flow, 'r') as f_flow:

    flow_data = json.load(f_flow)

    for i in range(0,len(flow_data)):   
        if "type" in flow_data[i].keys():
            if flow_data[i]["type"] == "tab":
                flow_id = flow_data[i]["id"]
            if flow_data[i]["type"] == "link in" and flow_data[i]["name"] == "metrics" :
                metrics_links_list = flow_data[i]["links"]
                metrics_id = flow_data[i]["id"]

    k=0 # aux int to iterate through metrics list
    #create all the nodes in each property cluster

    #flexdash has links with hex_id from other flows
    #flexdash_link_id = input("Enter the 8-bit hexadecimal node id from the flexdash link call: ")
    
    flexdash_link_id = "8cb87649afd62fd8" #testing

    for i in range(0,len(flow_data)):

        if "name" in flow_data[i].keys() and ("Property " in flow_data[i]["name"]) and (any(char.isdigit() for char in flow_data[i]["name"])):
            
            change_node = {
                "id": flow_data[i]["wires"][0][0],
                "type": "change",
                "z": flow_id,
                "name": "",
                "rules": [
                    {
                        "t": "set",
                        "p": "target",
                        "pt": "msg",
                        "to": "southbound.updateSubscriptions",
                        "tot": "str"
                    }
                ],
                "action": "",
                "property": "",
                "from": "",
                "to": "",
                "reg": False,
                "x": flow_data[i]["x"] + 400,
                "y": flow_data[i]["y"] - 40,
                "wires": [
                    [
                        secrets.token_hex(8)
                    ]
                ]
            }

            flow_data.append(change_node)

            link_node ={
                "id": change_node["wires"][0][0],
                "type": "link call",
                "z": flow_id,
                "name": "",
                "links": [],
                "linkType": "dynamic",
                "timeout": "30",
                "x": change_node["x"] + 400,
                "y": change_node["y"],
                "wires": [
                    []
                ]
            }

            flow_data.append(link_node)

            debug_node = {
                "id": flow_data[i]["wires"][0][1],
                "type": "debug",
                "z": flow_id,
                "name": "",
                "active": False,
                "tosidebar": True,
                "console": False,
                "tostatus": False,
                "complete": "true",
                "targetType": "full",
                "statusVal": "",
                "statusType": "auto",
                "x": flow_data[i]["x"] + 260,
                "y": flow_data[i]["y"] - 80,
                "wires": []
            }

            flow_data.append(debug_node)

            change_node2 = {
                "id": flow_data[i]["wires"][1][0],
                "type": "change",
                "z": flow_id,
                "name": "",
                "rules": [
                    {
                        "t": "set",
                        "p": "target",
                        "pt": "msg",
                        "to": "southbound.routed",
                        "tot": "str"
                    }
                ],
                "action": "",
                "property": "",
                "from": "",
                "to": "",
                "reg": False,
                "x": flow_data[i]["x"] + 400,
                "y": flow_data[i]["y"],
                "wires": [
                    [
                        secrets.token_hex(8)
                    ]
                ]
            }

            flow_data.append(change_node2)

            link_node2 = {
                "id": change_node2["wires"][0][0],
                "type": "link call",
                "z": flow_id,
                "name": "",
                "links": [],
                "linkType": "dynamic",
                "timeout": "30",
                "x": change_node2["x"] + 400,
                "y": change_node2["y"],
                "wires": [
                    []
                ]
            }

            flow_data.append(link_node2)

            broadcast_node = {
                "id": flow_data[i]["wires"][2][0],
                "type": "msg-router",
                "z": flow_id,
                "routerType": "broadcast",
                "topicDependent": False,
                "counterReset": False,
                "msgKeyField": "payload",
                "undefinedHash": False,
                "outputsInfo": [
                    {
                        "active": True,
                        "clone": False,
                        "delay": "0",
                        "weight": "0"
                    },
                    {
                        "active": True,
                        "clone": False,
                        "delay": "0",
                        "weight": "0"
                    }
                ],
                "name": "",
                "delaying": "unrelated",
                "msgControl": False,
                "outputs": 3,
                "x": flow_data[i]["x"] + 240,
                "y": flow_data[i]["y"] + 120,
                "wires": [
                    [
                        metrics_links_list[k]
                    ],
                    [
                        secrets.token_hex(8),
                        secrets.token_hex(8)
                    ],
                    [
                        secrets.token_hex(8)
                    ]
                ]

            }

            flow_data.append(broadcast_node)

            metrics_node ={
                "id": metrics_links_list[k],
                "type": "link out",
                "z": flow_id,
                "name": "metrics",
                "mode": "link",
                "links": [
                    metrics_id
                ],
                "x": flow_data[i]["x"] + 550,
                "y": flow_data[i]["y"] + 60,
                "wires": [],
                "l": True
            }

            flow_data.append(metrics_node)

            json_node={
                "id": broadcast_node["wires"][1][0],
                "type": "json",
                "z": flow_id,
                "name": "",
                "property": "payload.data",
                "action": "",
                "pretty": False,
                "x": flow_data[i]["x"] + 540,
                "y": flow_data[i]["y"] + 100,
                "wires": [
                    [
                        secrets.token_hex(8)
                    ]
                ]

            }

            flow_data.append(json_node)

            debug_node2 = {
                "id": broadcast_node["wires"][1][1],
                "type": "debug",
                "z": flow_id,
                "name": "",
                "active": False,
                "tosidebar": True,
                "console": False,
                "tostatus": False,
                "complete": "true",
                "targetType": "full",
                "statusVal": "",
                "statusType": "auto",
                "x": flow_data[i]["x"] + 700,
                "y": flow_data[i]["y"] + 60,
                "wires": []
            }

            flow_data.append(debug_node2)

            change_node3 = {
                "id": json_node["wires"][0][0],
                "type": "change",
                "z": flow_id,
                "name": "",
                "rules": [
                    {
                        "t": "set",
                        "p": "target",
                        "pt": "msg",
                        "to": "southbound.updateValue",
                        "tot": "str"
                    }
                ],
                "action": "",
                "property": "",
                "from": "",
                "to": "",
                "reg": False,
                "x": flow_data[i]["x"] + 730,
                "y": flow_data[i]["y"] + 100,
                "wires": [
                    [
                        secrets.token_hex(8)
                    ]
                ]
            }

            flow_data.append(change_node3)

            link_node3 = {
                "id": change_node3["wires"][0][0],
                "type": "link call",
                "z": flow_id,
                "name": "",
                "links": [],
                "linkType": "dynamic",
                "timeout": "30",
                "x": flow_data[i]["x"] + 890,
                "y": flow_data[i]["y"] + 100,
                "wires": [
                    []
                ]
            }

            flow_data.append(link_node3)

            flexdash_link_node = {
                "id": broadcast_node["wires"][2][0],
                "type": "link call",
                "z": flow_id,
                "name": "",
                "links": [
                    flexdash_link_id
                ],
                "linkType": "static",
                "timeout": "30",
                "x": flow_data[i]["x"] + 550,
                "y": flow_data[i]["y"] + 140,
                "wires": [
                    []
                ]
            }

            flow_data.append(flexdash_link_node)

            k += 1


with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)  


    
