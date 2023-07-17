import json
import tkinter as tk
import tkinter.filedialog
import secrets

history_length = "14400"

#directory for opening aasx and flow files
print("Please choose the asset file (.aasx)")
root = tk.Tk()
root.withdraw()
filepath_assetjson = tk.filedialog.askopenfilename(initialdir="./v3" ,title="Asset JSON file:")

f = open(filepath_assetjson)

#open aasx model file (json)
data = json.load(f)

coll_list = list()
evt_list = list()
evt_name = ""
n_properties_w_event = 0
metrics_link_list = list()

#check aas id, for property links
aas_id = data["assetAdministrationShells"][0]["identification"]["id"]
print("AAS ID: " + aas_id)

for i in range(0,len(data["submodels"])) :
    if data["submodels"][i]["idShort"] == "OperationalData":
        aas_opdata = data["submodels"][i]["submodelElements"]
        break

for i in range(0,len(aas_opdata)) :

    #Submodel Element Collections can have an indefinite number of events and subsequent collections inside
    #everytime a collection is found, add it to a list: coll_list
    if aas_opdata[i]["modelType"]["name"] == "SubmodelElementCollection":
        coll_list.append(aas_opdata[i]["value"])

    #look for events in aasx
    # j starts at 2:
    # 0 -> type: AssetAdministrationShell
    # 1 -> type: Submodel
    # 2 -> type: Property, take name from value

    if aas_opdata[i]["modelType"]["name"] == "BasicEvent":
        for j in range(2,len(aas_opdata[i]["observed"]["keys"])):
            
            #if it's the last element in list, add "Evt" to end, else add "." for multiple submodel element collections 
            if j == len(aas_opdata[i]["observed"]["keys"]) - 1:
                evt_name += aas_opdata[i]["observed"]["keys"][j]["value"] + "Evt"
            else:
                evt_name += aas_opdata[i]["observed"]["keys"][j]["value"] + "."
        
        n_properties_w_event +=1

        #add name of event to evt_list and then reset evt_name for next iteration
        evt_list.append(evt_name) 
        evt_name = ""    

# loop to check all submodel element collections in aasx
# keep adding collections to coll_list while they exist
while len(coll_list) != 0:

    #store the number of elements to check and delete after all checked
    initial_len = len(coll_list)

    #check each element in coll_list (SubmodelElementCollection)
    for i in range(0,len(coll_list)):
        for j in range(0,len(coll_list[i])):

            #if more collections exist inside this one, add to coll_list
            if coll_list[i][j]["modelType"]["name"] == "SubmodelElementCollection":
                coll_list.append(coll_list[i][j]["value"])
            
            #same as above (check events)
            if coll_list[i][j]["modelType"]["name"] == "BasicEvent":
                for k in range(2,len(coll_list[i][j]["observed"]["keys"])):
                    if k == len(coll_list[i][j]["observed"]["keys"])-1:
                        evt_name += coll_list[i][j]["observed"]["keys"][k]["value"] + "Evt"
                    else:
                        evt_name += coll_list[i][j]["observed"]["keys"][k]["value"] + "."
                
                n_properties_w_event +=1
                evt_list.append(evt_name) 
                evt_name = ""
    
    #after checking all initial elements in coll_list, delete them and start again if any new elements were added in j loop
    del coll_list[:initial_len]
          
print(evt_list)
f.close()

#-------------------------------------------------------------------------

#choose template flow file with no property nodes, so it can be populated
print("Please choose the template flow (.json)")
root = tk.Tk()
root.withdraw()
filepath_flow = tk.filedialog.askopenfilename(title="Node-Red flow JSON file:")

# v3 = create property handler, property nodes, trigger in, timestamps
# create before v2 (modular)

with open(filepath_flow, 'r') as f_flow:

    flow_data = json.load(f_flow)

    #search for flow id
    for i in range(0,len(flow_data)):   
        if "type" in flow_data[i].keys() and flow_data[i]["type"] == "tab":
            flow_id = flow_data[i]["id"]
    
    #create property handler subflow with all nodes and insert at the beginning of the flow (position is arbitrary)
    property_handler = {
        "id": "41b3a1439ccec2c1",
        "type": "subflow",
        "name": "Property handler",
        "info": "",
        "category": "",
        "in": [
            {
                "x": 260,
                "y": 520,
                "wires": [
                    {
                        "id": "95ca925e8f8cf880"
                    }
                ]
            }
        ],
        "out": [
            {
                "x": 1880,
                "y": 500,
                "wires": [
                    {
                        "id": "1274c1fecaa655a8",
                        "port": 0
                    },
                    {
                        "id": "78d0225e0b3a8fe6",
                        "port": 0
                    }
                ]
            },
            {
                "x": 1880,
                "y": 800,
                "wires": [
                    {
                        "id": "e62907e7bcbce663",
                        "port": 0
                    }
                ]
            },
            {
                "x": 1880,
                "y": 860,
                "wires": [
                    {
                        "id": "f02316f50a016d5d",
                        "port": 0
                    }
                ]
            }
        ],
        "env": [
            {
                "name": "PropertyName",
                "type": "str",
                "value": ""
            },
            {
                "name": "PropertyLink",
                "type": "str",
                "value": ""
            },
            {
                "name": "HistoryLength",
                "type": "num",
                "value": ""
            },
            {
                "name": "PropertyLinkEvt",
                "type": "str",
                "value": ""
            }
        ],
        "meta": {},
        "color": "#DDAA99",
        "status": {
            "x": 1740,
            "y": 700,
            "wires": [
                {
                    "id": "5f9633884f5e4cd4",
                    "port": 0
                }
            ]
        }
    }
    node1 = {
        "id": "127270a25c3d8888",
        "type": "switch",
        "z": "41b3a1439ccec2c1",
        "name": "topic",
        "property": "topic",
        "propertyType": "msg",
        "rules": [
            {
                "t": "eq",
                "v": "observe",
                "vt": "str"
            },
            {
                "t": "eq",
                "v": "unobserve",
                "vt": "str"
            },
            {
                "t": "eq",
                "v": "init",
                "vt": "str"
            }
        ],
        "checkall": "false",
        "repair": False,
        "outputs": 3,
        "x": 890,
        "y": 500,
        "wires": [
            [
                "1274c1fecaa655a8",
                "2cd93262147d3143"
            ],
            [
                "0f6603d9f95134b3",
                "78d0225e0b3a8fe6"
            ],
            [
                "0f6603d9f95134b3"
            ]
        ]
    }
    node2 = {
        "id": "1274c1fecaa655a8",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "PrepareOutput",
        "func": "var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {\n    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);\n    return v.toString(16);\n  });\n\n// Create an Observation Event Object ------------------------------------\nvar observation = {};\nobservation.id = uuid;\n//observation.source = msg.source;\nobservation.direction = \"Output\";\n\nvar observableReference = \"\";\n\n//var observedKeys = msg.payload.observed.keys;\n/*for(var key in observedKeys){\n    if(parseInt(key) < 2){\n        observableReference = observableReference + observedKeys[key].value + \"/\";\n    } else if (parseInt(key) >= 2 && parseInt(key) < (observedKeys.length - 1)) {\n        observableReference = observableReference + observedKeys[key].value + \".\";\n    } else {\n        observableReference = observableReference + observedKeys[key].value;\n    }\n}*/\n\nobservableReference = env.get(\"PropertyLink\");\n\nobservation.observableReference = observableReference;\n//observation.source = msg.req.params.aasid + \"/\" + msg.req.params.submodelId + \"/\" + msg.req.params.id;\nobservation.source = env.get(\"PropertyLinkEvt\");\n\nif(context.flow.get(\"timestamp\")){\n    observation.timestamp = context.flow.get(\"timestamp\");\n} else{\n    observation.timestamp = new Date().getTime();\n}\nobservation.payload = \"Data Flow Created\";\n//observation.href = msg.href;\n// END Create an Observation Object --------------------------------\n//outputMsgs.push(observation);\ncontext.flow.set('ObsObj', observation);\n//msg.payload = outputMsgs;\n//msg.payload = JSON.stringify(observation);\n//msg.test = JSON.parse(msg.payload);\nmsg.payload = observation;\nreturn msg;\n\n\n",
        "outputs": 1,
        "noerr": 0,
        "x": 1175,
        "y": 500,
        "wires": [
            []
        ],
        "l": False
    }
    node3 = {
        "id": "2cd93262147d3143",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "func": "msg.topic = \"control\";\nmsg.payload = \"open\";\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "x": 1175,
        "y": 540,
        "wires": [
            [
                "f894203f2fd3ac35",
                "5f9633884f5e4cd4"
            ]
        ],
        "l": False
    }
    node4 = {
        "id": "f894203f2fd3ac35",
        "type": "gate",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "controlTopic": "control",
        "defaultState": "closed",
        "openCmd": "open",
        "closeCmd": "close",
        "toggleCmd": "toggle",
        "defaultCmd": "default",
        "persist": False,
        "x": 1490,
        "y": 800,
        "wires": [
            [
                "e62907e7bcbce663"
            ]
        ]
    }
    node5 = {
        "id": "e62907e7bcbce663",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "func": "var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {\n    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);\n    return v.toString(16);\n});\nvar outMsg = {};\nvar ObsObj = context.flow.get('ObsObj');\nObsObj.id = uuid;\nvar timestamp = context.flow.get(\"$parent.timestamp\");\nif (typeof timestamp == 'undefined') {\n    timestamp = new Date().getTime();\n    ObsObj.timestamp = timestamp;\n}\nelse {\n    ObsObj.timestamp = timestamp;\n}\nObsObj.payload = context.flow.get(\"variable\");\noutMsg.payload = ObsObj;\nreturn outMsg;",
        "outputs": 1,
        "noerr": 0,
        "x": 1635,
        "y": 800,
        "wires": [
            []
        ],
        "l": False
    }
    node6 = {
        "id": "0f6603d9f95134b3",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "func": "msg.topic = \"control\";\nmsg.payload = \"close\";\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "x": 1175,
        "y": 660,
        "wires": [
            [
                "f894203f2fd3ac35",
                "5f9633884f5e4cd4"
            ]
        ],
        "l": False
    }
    node7 = {
        "id": "78d0225e0b3a8fe6",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "PrepareOutput",
        "func": "var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {\n    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);\n    return v.toString(16);\n  });\n\n// Create an Observation Event Object ------------------------------------\nvar observation = {};\nobservation.id = uuid;\nobservation.source = msg.source;\nobservation.direction = \"Output\";\nvar observableReference = \"\";\n\n/*var observedKeys = msg.payload.observed.keys;\nfor (var key in observedKeys) {\n    if (parseInt(key) < 2) {\n        observableReference = observableReference + observedKeys[key].value + \"/\";\n    } else if (parseInt(key) >= 2 && parseInt(key) < (observedKeys.length - 1)) {\n        observableReference = observableReference + observedKeys[key].value + \".\";\n    } else {\n        observableReference = observableReference + observedKeys[key].value;\n    }\n}*/\n\nobservableReference = env.get(\"PropertyLink\");\n\nobservation.observableReference = observableReference;\n//observation.source = msg.req.params.aasid + \"/\" + msg.req.params.submodelId + \"/\" + msg.req.params.id;\nobservation.source = env.get(\"PropertyLinkEvt\");\n\nif(context.flow.get(\"timestamp\")){\n    observation.timestamp = context.flow.get(\"timestamp\");\n} else{\n    observation.timestamp = new Date().getTime();\n}\nobservation.payload = \"Data Flow removed\";\n//observation.href = msg.href;\n// END Create an Observation Object --------------------------------\n//outputMsgs.push(observation);\n\n//msg.payload = outputMsgs;\n//msg.payload = JSON.stringify(observation);\n//msg.test = JSON.parse(msg.payload);\ncontext.flow.set(\"ObsObj\", \"\");\nmsg.payload = observation;\nreturn msg;\n\n\n",
        "outputs": 1,
        "noerr": 0,
        "x": 1175,
        "y": 600,
        "wires": [
            []
        ],
        "l": False
    }
    node8 = {
        "id": "96b701c2b50dc6f7",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "func": "var propertyName = env.get(\"PropertyName\");\nvar Outmsg = {};\nOutmsg.topic = msg.topic;\nvar variable = context.flow.get(\"$parent.\" + propertyName);\ncontext.flow.set(\"variable\", variable);\n\nOutmsg.payload = variable;\nreturn Outmsg;\n",
        "outputs": 1,
        "noerr": 0,
        "x": 875,
        "y": 800,
        "wires": [
            [
                "f894203f2fd3ac35",
                "f02316f50a016d5d"
            ]
        ],
        "l": False
    }
    node9 = {
        "id": "f02316f50a016d5d",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "responseTime",
        "func": "var historyArrayName = \"$parent.\" + env.get(\"PropertyName\") + \"_hist\";\nvar outMsg = {};\noutMsg.topic = \"put\";\nvar timestamp = context.flow.get(\"$parent.timestamp\");\nif (typeof timestamp == \"undefined\") {\n    timestamp = new Date().getTime();\n}\noutMsg.payload = {\n    link: env.get(\"PropertyLink\"),\n    tstamp: timestamp,\n    data: context.flow.get(\"variable\")\n};\nlet history = context.flow.get(historyArrayName) || [];\nif (history.length >= env.get(\"HistoryLength\")) {\n    history.pop();\n}\nhistory.push(outMsg.payload);\ncontext.flow.set(historyArrayName, history);\nreturn outMsg;",
        "outputs": 1,
        "noerr": 0,
        "x": 1075,
        "y": 860,
        "wires": [
            []
        ],
        "l": False
    }
    node10 = {
        "id": "95ca925e8f8cf880",
        "type": "switch",
        "z": "41b3a1439ccec2c1",
        "name": "scheduler",
        "property": "topic",
        "propertyType": "msg",
        "rules": [
            {
                "t": "neq",
                "v": "sbi scheduling data routing",
                "vt": "str"
            },
            {
                "t": "else"
            }
        ],
        "checkall": "false",
        "repair": False,
        "outputs": 2,
        "x": 440,
        "y": 520,
        "wires": [
            [
                "127270a25c3d8888"
            ],
            [
                "96b701c2b50dc6f7"
            ]
        ]
    }
    node11 = {
        "id": "5f9633884f5e4cd4",
        "type": "unsafe-function",
        "z": "41b3a1439ccec2c1",
        "name": "",
        "func": "if(msg.payload == \"open\"){\n    msg.payload = ({ fill: \"green\", text: \"Open\" });\n} else if (msg.payload == \"close\"){\n    msg.payload = ({ fill: \"red\", text: \"Closed\" });\n}\n\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "x": 1535,
        "y": 700,
        "wires": [
            []
        ],
        "l": False
    }

    flow_data.insert(0,property_handler)
    flow_data.insert(1,node1)
    flow_data.insert(2,node2)
    flow_data.insert(3,node3)
    flow_data.insert(4,node4)
    flow_data.insert(5,node5)
    flow_data.insert(6,node6)
    flow_data.insert(7,node7)
    flow_data.insert(8,node8)
    flow_data.insert(9,node9)
    flow_data.insert(10,node10)
    flow_data.insert(11,node11)

    #position of initial trigger_in node (top left)
    x_pos = 185
    y_pos = 480

    #populate links in trigger_out with the number of properties in file
    for i in range(0,len(flow_data)):

        if "name" in flow_data[i].keys() and flow_data[i]["name"] == "trigger_out":

            for p in range(n_properties_w_event):

                #generate property trigger ids
                property_trigger_id = secrets.token_hex(8)

                #add the node id of every property trigger in node to links in trigger out
                flow_data[i]["links"].append(property_trigger_id)

                #create each trigger_in, property and timestamp nodes here

                trigger_in_node = {
                    "id": property_trigger_id,
                    "type": "link in",
                    "z": flow_id,
                    "name": "trigger_in_" + str(p+1),
                    "links": [
                        flow_data[i]["id"]
                    ],
                    "x": x_pos,
                    "y": y_pos,
                    "wires": [
                        [
                            secrets.token_hex(8)
                        ]
                    ]
                }

                flow_data.append(trigger_in_node)

                observe_node = {
                    "id": secrets.token_hex(8),
                    "type": "inject",
                    "z": flow_id,
                    "name": "",
                    "props": [
                        {
                            "p": "payload"
                        },
                        {
                            "p": "topic",
                            "vt": "str"
                        }
                    ],
                    "repeat": "",
                    "crontab": "",
                    "once": False,
                    "onceDelay": 0.1,
                    "topic": "observe",
                    "payload": "",
                    "payloadType": "date",
                    "x": trigger_in_node["x"] - 10,
                    "y": trigger_in_node["y"] + 60,
                    "wires": [
                        [
                            trigger_in_node["wires"][0][0]
                        ]
                    ]
                }

                flow_data.append(observe_node)

                unobserve_node = {
                    "id": secrets.token_hex(8),
                    "type": "inject",
                    "z": flow_id,
                    "name": "",
                    "props": [
                        {
                            "p": "payload"
                        },
                        {
                            "p": "topic",
                            "vt": "str"
                        }
                    ],
                    "repeat": "",
                    "crontab": "",
                    "once": False,
                    "onceDelay": 0.1,
                    "topic": "unobserve",
                    "payload": "",
                    "payloadType": "date",
                    "x": trigger_in_node["x"] - 25,
                    "y": trigger_in_node["y"] + 100,
                    "wires": [
                        [
                            trigger_in_node["wires"][0][0]
                        ]
                    ]
                }

                flow_data.append(unobserve_node)

                init_node = {
                    "id": secrets.token_hex(8),
                    "type": "inject",
                    "z": flow_id,
                    "name": "",
                    "props": [
                        {
                            "p": "payload"
                        },
                        {
                            "p": "topic",
                            "vt": "str"
                        }
                    ],
                    "repeat": "",
                    "crontab": "",
                    "once": True,
                    "onceDelay": 0.1,
                    "topic": "init",
                    "payload": "",
                    "payloadType": "date",
                    "x": trigger_in_node["x"] - 5,
                    "y": trigger_in_node["y"] + 140,
                    "wires": [
                        [
                            trigger_in_node["wires"][0][0]
                        ]
                    ]
                }

                flow_data.append(init_node)

                property_node = {
                    "id": trigger_in_node["wires"][0][0],
                    "type": "subflow:41b3a1439ccec2c1",
                    "z": flow_id,
                    "name": "Property " + str(p+1),
                    "x": trigger_in_node["x"] + 165,
                    "y": trigger_in_node["y"],
                    "wires": [
                        [],
                        [],
                        []
                    ]
                }

                flow_data.append(property_node)

                #if current property number is uneven, the next is even, meaning only x position changes
                #else next is uneven, meaning x position goes back to initial and y position increments

                #like so:
                # (x,y)                 (x+i, y)
                # (x, y+j)              (x+i, y+j)
                # Property 1            Property 2
                # Property 3            Property 4
                # Property 5            Property 6
                # Property 7            Property 8
                # Property 9            Property 10
                
                if (p+1)%2 == 1:
                    x_pos = 1725 #x_pos + 1540
                else:
                    x_pos = 185 #x_pos - 1540
                    y_pos = y_pos + 320
                
#write all changes to file
with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)

#open again to fill the property nodes
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
                

#write all changes to file
with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)


#open file again and create all other nodes
with open(filepath_flow, 'r') as f_flow:

    flow_data = json.load(f_flow)

    for i in range(0,len(flow_data)):   
        if "type" in flow_data[i].keys():
            if flow_data[i]["type"] == "link in" and flow_data[i]["name"] == "metrics" :
                metrics_id = flow_data[i]["id"]
                metrics_node_pos = i

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
                        secrets.token_hex(8)
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
                "id": broadcast_node["wires"][0][0],
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

            metrics_link_list.append(metrics_node["id"])

    for m in metrics_link_list:
        flow_data[metrics_node_pos]["links"].append(m)

            
#write all changes to file
with open(filepath_flow, 'w') as f_flow:
    json.dump(flow_data, f_flow)  


    
