from cgi import print_arguments
from hashlib import new
from lib2to3.pygram import python_grammar_no_print_statement
from nis import match
import re
import json
from property.location.location_views import db

required_fields = {
    "area":[],
    "estate_status":[],
    "apartment":[],
    "furniture":["WITH FULL FURNITURE", "Fully Furnished","Semi Furnished","luxurious furnished","furnished","Renovated"],
    "property_type":[],
}

mapping_db = {
    "area":["area_name",db.property_area.find({},{"area_name":1,"_id":0})],
    "estate_status":["estate_status_name",db.property_estatestatus.find({},{"estate_status_name":1,"_id":0})],
    "apartment":["apartment_name",db.property_apartment.find({},{"apartment_name":1,"_id":0})],
    "property_type":["type_name",db.property_estate_type.find({},{"type_name":1,"_id":0})]
}

def findOptimized(required_fields,mapping_db):
    for key,value  in mapping_db.items(): 
        required_fields[key] = [ x[value[0]].lower() for x in   list(value[1]) ]
    

    return required_fields


def checkisdigit(inputstring):
    if True in [char.isdigit() for char in inputstring]:
        return True
    else:
        return False


def findMobile(inputstring):
    pattern = re.compile(r"\d{10}")
    if re.search(pattern=pattern, string=inputstring) :
        return re.findall(pattern=pattern,string= inputstring)
    else:
        return []

def findBigNumbers(inputstring):
    pattern = re.compile(r"[1-9]\d{3,10}")
    if re.search(pattern=pattern, string=inputstring) :
        numbers = re.findall(pattern=pattern,string= inputstring)
        numbers = [int(x) for x in numbers]
        return numbers
    else:
        return []

def find_match(SizeInput,size_matches):
    if size_matches[0] in SizeInput:
        return SizeInput
    sizelist = SizeInput.split(" ")
    matches = []
    mul =1
    for i in sizelist:
        if checkisdigit(i):
            matches.append(float(i))
        elif i in ["lk","Lac","lakh","lak","lacs","lakhs"]:
            mul = 100000
        elif i in ["cr"]:
            mul = 10000000
    if len(matches):
        return matches[0]*mul


def findOwner(input):
    pattern = re.compile(r"\d{5}[-\.\s]??\d{5}")
    pattern2 = re.compile(r"\d{1,2}:\d{2}\s['am]','pm]']")
    pattern1 = re.compile(r"\d{2}/\d{2}")

    if (re.search(pattern=pattern1, string=input) and re.search(pattern=pattern2, string=input)) or re.search(pattern=pattern, string=input) :
        mobiles = re.findall(pattern=pattern,string=input)

        return True,mobiles[0].replace(" ","")
    else:
        return False,False


def cleaningLine(i):
    i = i.replace("/"," ")
    if i != "\n":
        i= i.strip()
        i = i.rstrip(",.\n")
        i= i.strip()
        i = i.rstrip(",.\n")
        i = i.lstrip("👉 ")
        i = i.lstrip("*♦️")
        #print(i)
    for k in i:
        fv = ["*",",","@","-"]
        if k in fv:
            i = i.replace(k,"")
        if "sqft" in i.lower():
            i = i.replace(":","")
    
    return i

def findHouse(input):
    pattern = re.compile(r"\d{1}[-\.\s\,][-\.\s\,]}\d{0,1}[-\.\s]??\D{8}|\d{1,6}\D{3,20}|\d{1,6}[,\.]\d{1,6}[,\.]\s{0,1}\D{1,10}|\d{1,6}[,\.]\s{0,1}\D{1,10}")
    #pattern = re.compile(r"|\d{3}[-\.\,\s]{2}??\D{4,5}")
    houselist = re.findall(pattern=pattern, string=input)
    false_values = ["+", ":","pm]","am]"]
    filterhouse = []
    for i in false_values:
        filterhouse = filterhouse + [ x for x in houselist if i  in x  ]
    return set(houselist)- set(filterhouse)


def removeX(input):
    i =input
    x_ind = -1
    x_list = [" X "," × ", "X","x","×"]
    for x in x_list:
        if x in i:
            #print(x)
            x_ind = i.find(x)
            if " " in x:
                i = i.replace(x,x.strip())
                #print(i)
                x_ind = i.find(x.strip())
                #print(x_ind)

    if x_ind != -1:
        s_index = i[:x_ind].rfind(" ")
        s1_index = i[x_ind:].find(" ")
        #print(s_index,s1_index)
        if(s_index !=-1):
            n1 = i[s_index:x_ind].strip()
        else:
            n1 = i[:x_ind].strip()
        if(s1_index ==-1):
            n2 = i[x_ind+1:].strip()
        else:
            n2 = i[x_ind+1:x_ind+s1_index].strip()
        
        if n1.isdigit() and n2.isdigit():
            mul = int(n1) * int(n2)
            return mul
    return None

def filterRooms(mydict):
    room_list = []
    for j,i in enumerate(mydict["number_of_bedrooms"]):
        bhk_index = i.find("bhk")
        if bhk_index!= -1:
            mydict["number_of_bedrooms"][j]  = i[:bhk_index]
            mydict["number_of_bedrooms"][j] = mydict["number_of_bedrooms"][j].replace(" ","")
            room_list.append(int(mydict["number_of_bedrooms"][j]))

        else:
            size_matches = ["Sq. Yards" ,"sq yard","Sq yards","sq","carpet","ft","Sf","SFT","SB","SQFT","var", "Square","feet","vaar","VINGA"]
            size_matches = [ x.lower() for x in size_matches ]
            price_matches = ["lk","Lac","lakh", "cr","lak","lacs"]
            price_matches = [ x.lower() for x in price_matches ]
            
            
            if any(x in mydict["number_of_bedrooms"][j] for x in size_matches):
                size_match = find_match(mydict["number_of_bedrooms"][j],size_matches)
                if "floor_space" in mydict.keys():
                    mydict["floor_space"].append(size_match)
                else:
                    mydict["floor_space"] = [size_match]
        
            elif any(x in mydict["number_of_bedrooms"][j] for x in price_matches):
                if "budget" in mydict.keys():
                    mydict["budget"].append(find_match(mydict["number_of_bedrooms"][j],price_matches))
                else:
                    mydict["budget"] = [find_match(mydict["number_of_bedrooms"][j],price_matches)]
                
            else:
                if "Others" in mydict.keys():
                    mydict["Others"].append(mydict["number_of_bedrooms"][j])
                else:
                    mydict["Others"] = [mydict["number_of_bedrooms"][j]]
    mydict["number_of_bedrooms"] = room_list
    print(mydict["number_of_bedrooms"])
def filterOthers(mydict):
    if "Others" in mydict.keys():
        for j,i in enumerate(mydict["Others"]):
            if findBigNumbers(mydict["Others"][j]) :
                if "budget" in mydict.keys():
                    mydict["budget"] + findBigNumbers(mydict["Others"][j])
                else:
                    mydict["budget"] = findBigNumbers(mydict["Others"][j])


def findSize(input):
    pattern = re.compile(r"\d{1,4}\s{0,1}[X,x,×]\s{0,1}\d{1,4}")
    #pattern = re.compile(r"|\d{3}[-\.\,\s]{2}??\D{4,5}")
    sl = re.findall(pattern=pattern, string=input)
    filtersl = []
    for i in sl:
        if removeX(i) is not None:
            filtersl.append(removeX(i))
    return filtersl

def findBudget(input):
    keywords=["lk","Lac","lakh", "cr"]
    inputlist = input.split(" ")
    typelist = []
    keywords = [ x.lower() for x in keywords ]
    for i in keywords:
        if i in inputlist:
            typelist.append(i)
    return typelist

def findType(input):
    keywords=["purchase","lena","rent", "sell","kharid","sale"]
    inputlist = input.split(" ")
    typelist = []
    for i in keywords:
        if i in inputlist:
            typelist.append(i)
    
    return typelist

#societylist = apartment.objects.all()
societylist = ["Royal Paradise","Keshav Narayan","Raj Harmoney","Grandza","Rayaltone","Sun Sine Residency","Anupam hieght","Dev bhoomi","Sns splendid","Hitek Avenue","Surya green view","Next orchied","Veer exotica","CAPITAL GREENS","ECO GARDEN","SANGINI","OFIRA RESIDENCY" ,"RAJHANS","Srungal Solitaire","Rajhans Royalton","utsav","meera","marvela","Aakash expression","SURYA PRAKASH RESIDENCY",
"NISRAG AAPRMENT","RAJTILAK AAPRMENT","SURYA PLEASE","AARNAV APRMENT","SURYA DARSAN","KPM RESIDENCY","MURTI RESIDENCY","FALCAN AVENUE","AASHIRWAD PARK","GOLDEN AVENUE","PADMA KURTI","SHIMANDAR APPRMENT" ,"BAGVTI ASHISH" ,"MEGNA PARK","SHITAL PARK","NAVPAD AAPRMENT" ,"SURYA COMPLEX" ,"PALACIO","KESHAV NARAYNA","OPERA HOUSE","AARJAV AAPRMENT","MAAHI RESIDENCY","MAGH SHARMAND","SAKAR RESIDENCY","MURLIDHAR","SANGINI RESIDENCY"]
rf =  findOptimized(required_fields,mapping_db)

def findArea(input):
    keywords=["VESU","CITYLIGHT","PIPILOD", "NEW CITYLIGHT ROAD","PARLE POINT","Ghod Dod","Bhatar Road","v I P road","vIP road","ring road","palanpur","palgam","new city light","Mansarovar","PARVAT PATIA","GODADARA","althan","CITy light","Pandesara GIDC","adajan","Ghod Dhod Road","vackanja","Pal","Athwalines","Udhana","Kadodara","Udhna"]
    inputlist = input.split(" ")
    keywords = [ x.lower() for x in keywords ]
    typelist = []
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist


def findSociety(input):
    inputlist = input.split(" ")
    keywords = [ x.lower() for x in rf["apartment"] ]
    typelist = []
    for i in keywords:
        # so = fuzz.ratio(i,inputlist)
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist

def findFurntiure(input):
    keywords=["WITH FULL FURNITURE", "Fully Furnished","Semi Furnished","luxurious furnished","furnished","Renovated"]
    inputlist = input.split(" ")
    typelist = []
    keywords = [ x.lower() for x in keywords ]
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
            break
    return typelist

def findPropertyType(input):
    keywords=["Flat","plot","shop","rowhouse","Ro-House","Bunglows","office","Bunglow","ROW HOUSE","Bungalow","Banglow","Shed","Lend","Godown","warehouse","land","House"]
    inputlist = input.split(" ")
    #print(inputlist)
    typelist = []
    keywords = [ x.lower() for x in keywords ]
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
            break
    return typelist    

def findALlRequiremnts(lines,start_index):
    myDict = dict()
    prevHouse = start_index

    myDict[start_index] = dict()
    for j,i in enumerate(lines[start_index:]):
        #print(prevHouse,j,start_index,i)
        if findOwner(i) and j != 0:
            #myDict[prevHouse]["Newquery"] = "true"
            return myDict, start_index+j
        else:
            i= cleaningLine(i).lower() 
            #print(len(findArea(i)) , len(findType(i)) , findHouse(i) ,len(findPropertyType(i)), findSociety(i))
            if i == "\n":
                #print("blank")
                prevHouse = start_index+j
                myDict[prevHouse] = dict()
                    

            else:
                if len(findArea(i)) or  len(findType(i)) or len(findHouse(i)) or len(findPropertyType(i)) or len(findSociety(i)) or len(findMobile(i)) :
                    if len(findHouse(i)):
                        if "number_of_bedrooms" in myDict[prevHouse].keys():
                            myDict[prevHouse]["number_of_bedrooms"] = myDict[prevHouse]["number_of_bedrooms"]+ list(findHouse(i))
                        else:
                            myDict[prevHouse]["number_of_bedrooms"] = list(findHouse(i))
                    if "area" in myDict[prevHouse].keys():
                        myDict[prevHouse]["area"] = myDict[prevHouse]["area"]+findArea(i)
                    elif len(findArea(i)):
                        myDict[prevHouse]["area"] = findArea(i)
                    
                    if "estate_status" in myDict[prevHouse].keys():
                        myDict[prevHouse]["estate_status"] = myDict[prevHouse]["estate_status"]+findType(i)
                    elif len(findType(i)):
                        myDict[prevHouse]["estate_status"] = findType(i)
                    
                    if "apartment" in myDict[prevHouse].keys():
                        myDict[prevHouse]["apartment"] = myDict[prevHouse]["apartment"]+findSociety(i)
                    elif len(findSociety(i)):
                        myDict[prevHouse]["apartment"] = findSociety(i)

                    if "estate_type" in myDict[prevHouse].keys():
                        myDict[prevHouse]["estate_type"] = myDict[prevHouse]["estate_type"]+findPropertyType(i)
                    elif len(findPropertyType(i)):
                        myDict[prevHouse]["estate_type"] = findPropertyType(i)
                    
                    if "broker_mobile" in myDict[prevHouse].keys():
                        myDict[prevHouse]["broker_mobile"] = myDict[prevHouse]["broker_mobile"]+findMobile(i)
                    elif len(findMobile(i)):
                        myDict[prevHouse]["broker_mobile"] = findMobile(i)
                        myDict[prevHouse]["endquery"] = "true"
                    
                    if len(findSize(i)):
                        if "floor_space" in myDict[prevHouse].keys():
                            myDict[prevHouse]["floor_space"] = myDict[prevHouse]["floor_space"]+ list(findSize(i))
                        else:
                            myDict[prevHouse]["floor_space"] = list(findSize(i))

                    if len(findFurntiure(i)):
                        myDict[prevHouse]["Furniture"] = findFurntiure(i)
                else:
                    if "Others" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Others"].append(i)
                    else:
                        myDict[prevHouse]["Others"] = [i]
    return myDict, start_index+j

def filterSize(mydict):

    if "number_of_bedrooms" in mydict.keys():
        print("Here1")
        mydict["number_of_bedrooms"] = [ x.lower() for x in mydict["number_of_bedrooms"] ]
        filterRooms(mydict)
        print("mydict",mydict)
    if "Others" in mydict.keys():
        filterOthers(mydict)
    


def get_data_from_msg(string):
    lines  = string.split("\n")
    start_index =0
    end_index = 0
    i=0
    print(len(lines))
    owner = "7984702696"
    new_dic = dict()
    json_index = []
    while i < len(lines):
        json_index = findALlRequiremnts(lines,i)
        # print("json_index",json_index)
        # print(i)
        if findOwner(lines[i])[0]:
            owner = findOwner(lines[i])[1]
            # print("owner",owner)
            json_index[0][list(json_index[0].keys())[0]]["Newquery"] = {"found":"true"}
            if owner not in new_dic.keys():
                new_dic[owner] = [json_index[0]]
            else:
                new_dic[owner].append(json_index[0])
            end_index = json_index[1]
            if i!= end_index:
                i = end_index
            else:
                i=i+1
        elif lines[i] == "\n":
            i=i+1
        else:
            print("json_index",json_index)
            if owner in new_dic.keys():
                new_dic[owner].append(json_index[0])
            else:
                new_dic[owner] = [json_index[0]]
            i =i+1

    print("new_dic",new_dic)
    jsonlist = dict()

    prev_json = dict()
    for i in new_dic.keys():
        for j in  range(0, len(new_dic[i])):
            #print(new_dic[i][j])
            for k in new_dic[i][j].keys():
                
                filterSize(new_dic[i][j][k])
                print("n",new_dic[i][j][k])
                
                # print("prev_json" , prev_json)
                present_json = new_dic[i][j][k]
                # print("present_json",present_json)
                if "Newquery" in present_json.keys() and "endquery" not in present_json.keys():
                    prev_json = present_json

                if "endquery" in prev_json.keys():
                    prev_json = present_json

                if len(prev_json.keys()) and prev_json != present_json:
                    for key in prev_json.keys():
                        if not key in new_dic[i][j][k]:
                            if key in ["estate_status","estate_type","broker_mobile","budget","apartment","Others","floor_space"]:
                                new_dic[i][j][k][key] = prev_json[key]

                            elif key == "area" and (("estate_type" in prev_json.keys() or "estate_type" in present_json.keys() ) or ("Newquery" in prev_json.keys()) or len(prev_json.keys())==1):
                                new_dic[i][j][k][key] = prev_json[key]

                            elif key in ["number_of_bedrooms","Furniture"] and (("estate_type" in present_json.keys() and present_json["estate_type"][0] not in ["PLOT"]) or ("estate_type" not in present_json.keys()) ):
                                new_dic[i][j][k][key] = prev_json[key]
                        
                        else:
                            if prev_json[key] != present_json[key]:
                                new_dic[i][j][k][key] = list(set(prev_json[key]+present_json[key]))
                
                
                
                # print(new_dic[i][j][k])
                prev_json  = new_dic[i][j][k]
                # print("prev_json",prev_json)
                if i in jsonlist.keys():
                    jsonlist[i].append(prev_json)
                else:
                    jsonlist[i] = [prev_json]

    print(jsonlist)
    validlist = dict()
    for key in jsonlist.keys():
        for i,jobject in enumerate(jsonlist[key]):
            if "endquery" in jobject.keys():
                if "broker_mobile" in jsonlist[key][i-1].keys():
                        jsonlist[key][i-1]["broker_mobile"] = jsonlist[key][i-1]["broker_mobile"] + jsonlist[key][i]["broker_mobile"]
                else:
                    jsonlist[key][i-1]["broker_mobile"] = jsonlist[key][i]["broker_mobile"]
                if key in validlist.keys():
                    validlist[key].append(jsonlist[key][i-1])
                else:
                    validlist[key] = [jsonlist[key][i-1]]
            

            


    
    json_object = json.dumps(validlist, sort_keys=True, indent = 4) 
    with open("samplequery2.json", "w") as outfile:
        outfile.write(json_object)

    # print(validlist)
    if not validlist:
        if key in validlist.keys():
            validlist[key].append(jsonlist[key][0])
        else:
            validlist[key] = [jsonlist[key][0]]
    return validlist

#print(jsonlist)

