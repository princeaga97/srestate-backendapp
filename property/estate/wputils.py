from cgi import print_arguments
from hashlib import new
from lib2to3.pygram import python_grammar_no_print_statement
from nis import match
import re
import json

def checkisdigit(inputstring):
    if True in [char.isdigit() for char in inputstring]:
        return True
    else:
        return False

def differnce_dict(dict1, dict2):
    set1 = set(dict1.items())
    set2 = set(dict2.items())
    return set1 - set2

def findMobile(inputstring):
    pattern = re.compile(r"\d{10}")
    if re.search(pattern=pattern, string=inputstring) :
        return re.findall(pattern=pattern,string= inputstring)
    else:
        return []

def find_match(SizeInput,size_matches):
    if size_matches[0] in SizeInput:
        return SizeInput
    sizelist = SizeInput.split(" ")
    matches = []
    for i in sizelist:
        i = i.strip()
        if checkisdigit(i.strip(".\n")):
            matches.append(i)
        elif i in size_matches:
            matches.append(i)
    
    if len(matches):
        return " ".join(matches)


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
            i = i.replace(k," ")
        if "SQFT" in i.upper():
            i = i.replace(":","")
    
    return i

def findHouse(input):
    pattern = re.compile(r"\d{1}[-\.\s\,][-\.\s\,]}\d{0,1}[-\.\s]??\D{8}|\d{1,6}\D{3,20}|\d{1,6}[,\.]\d{1,6}[,\.]\s{0,1}\D{1,10}|\d{1,6}[,\.]\s{0,1}\D{1,10}")
    #pattern = re.compile(r"|\d{3}[-\.\,\s]{2}??\D{4,5}")
    houselist = re.findall(pattern=pattern, string=input)
    false_values = ["+", ":","PM]","AM]"]
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
    for j,i in enumerate(mydict["Rooms"]):
        bhk_index = i.find("BHK")
        if bhk_index!= -1:
            mydict["Rooms"][j]  = i[:bhk_index+3]
            mydict["Rooms"][j].replace(" ","")
            room_list.append(mydict["Rooms"][j])

        else:
            size_matches = ["Sq. Yards" ,"sq yard","Sq yards","sq","carpet","ft","Sf","SFT","SB","SQFT","var", "Square","feet","vaar","VINGA"]
            size_matches = [ x.upper() for x in size_matches ]
            price_matches = ["lk","Lac","lakh", "cr","lak","lacs"]
            price_matches = [ x.upper() for x in price_matches ]
            
            
            if any(x in mydict["Rooms"][j] for x in size_matches):
                if "Size" in mydict.keys():
                    mydict["Size"].append( find_match(mydict["Rooms"][j],size_matches))
                else:
                    mydict["Size"] = [ find_match(mydict["Rooms"][j],size_matches)]
        
            elif any(x in mydict["Rooms"][j] for x in price_matches):
                if "Budget" in mydict.keys():
                    mydict["Budget"].append(find_match(mydict["Rooms"][j],price_matches))
                else:
                    mydict["Budget"] = [find_match(mydict["Rooms"][j],price_matches)]
                
            else:
                if "Others" in mydict.keys():
                    mydict["Others"].append(mydict["Rooms"][j])
                else:
                    mydict["Others"] = [mydict["Rooms"][j]]
                
        
    mydict["Rooms"] = room_list

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
    keywords = [ x.upper() for x in keywords ]
    for i in keywords:
        if i in inputlist:
            typelist.append(i)
    return typelist

def findType(input):
    keywords=["PURCHASE","LENA","RENT", "SELL","KHARID","SALE"]
    inputlist = input.split(" ")
    typelist = []
    for i in keywords:
        if i in inputlist:
            typelist.append(i)
    
    return typelist

societylist = ["Royal Paradise","Keshav Narayan","Raj Harmoney","Grandza","Rayaltone","Sun Sine Residency","Anupam hieght","Dev bhoomi","Sns splendid","Hitek Avenue","Surya green view","Next orchied","Veer exotica","CAPITAL GREENS","ECO GARDEN","SANGINI","OFIRA RESIDENCY" ,"RAJHANS","Srungal Solitaire","Rajhans Royalton","utsav","meera","marvela","Aakash expression","SURYA PRAKASH RESIDENCY",
"NISRAG AAPRMENT","RAJTILAK AAPRMENT","SURYA PLEASE","AARNAV APRMENT","SURYA DARSAN","KPM RESIDENCY","MURTI RESIDENCY","FALCAN AVENUE","AASHIRWAD PARK","GOLDEN AVENUE","PADMA KURTI","SHIMANDAR APPRMENT" ,"BAGVTI ASHISH" ,"MEGNA PARK","SHITAL PARK","NAVPAD AAPRMENT" ,"SURYA COMPLEX" ,"PALACIO","KESHAV NARAYNA","OPERA HOUSE","AARJAV AAPRMENT","MAAHI RESIDENCY","MAGH SHARMAND","SAKAR RESIDENCY","MURLIDHAR","SANGINI RESIDENCY"]


def findArea(input):
    keywords=["VESU","CITYLIGHT","PIPILOD", "NEW CITYLIGHT ROAD","PARLE POINT","Ghod Dod","Bhatar Road","v I P road","vIP road","ring road","palanpur","palgam","new city light","Mansarovar","PARVAT PATIA","GODADARA","althan","CITy light","Pandesara GIDC","adajan","Ghod Dhod Road","vackanja","Pal","Athwalines","Udhana","Kadodara","Udhna"]
    inputlist = input.split(" ")
    keywords = [ x.upper() for x in keywords ]
    typelist = []
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist


def findSociety(input):
    inputlist = input.split(" ")
    keywords = [ x.upper() for x in societylist ]
    typelist = []
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist

def findFurntiure(input):
    keywords=["WITH FULL FURNITURE", "Fully Furnished","Semi Furnished","luxurious furnished","furnished","Renovated"]
    inputlist = input.split(" ")
    typelist = []
    keywords = [ x.upper() for x in keywords ]
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
    keywords = [ x.upper() for x in keywords ]
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
            i= cleaningLine(i).upper() 
            #print(len(findArea(i)) , len(findType(i)) , findHouse(i) ,len(findPropertyType(i)), findSociety(i))
            if i == "\n":
                #print("blank")
                prevHouse = start_index+j
                myDict[prevHouse] = dict()
                    

            else:
                if len(findArea(i)) or  len(findType(i)) or len(findHouse(i)) or len(findPropertyType(i)) or len(findSociety(i)) or len(findMobile(i)) :
                    if len(findHouse(i)):
                        if "Rooms" in myDict[prevHouse].keys():
                            myDict[prevHouse]["Rooms"] = myDict[prevHouse]["Rooms"]+ list(findHouse(i))
                        else:
                            myDict[prevHouse]["Rooms"] = list(findHouse(i))
                    if "Area" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Area"] = myDict[prevHouse]["Area"]+findArea(i)
                    elif len(findArea(i)):
                        myDict[prevHouse]["Area"] = findArea(i)
                    
                    if "Type" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Type"] = myDict[prevHouse]["Type"]+findType(i)
                    elif len(findType(i)):
                        myDict[prevHouse]["Type"] = findType(i)
                    
                    if "Society" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Society"] = myDict[prevHouse]["Society"]+findSociety(i)
                    elif len(findSociety(i)):
                        myDict[prevHouse]["Society"] = findSociety(i)

                    if "PropertyType" in myDict[prevHouse].keys():
                        myDict[prevHouse]["PropertyType"] = myDict[prevHouse]["PropertyType"]+findPropertyType(i)
                    elif len(findPropertyType(i)):
                        myDict[prevHouse]["PropertyType"] = findPropertyType(i)
                    
                    if "Mobile" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Mobile"] = myDict[prevHouse]["Mobile"]+findMobile(i)
                    elif len(findMobile(i)):
                        myDict[prevHouse]["Mobile"] = findMobile(i)
                        myDict[prevHouse]["endquery"] = "true"
                    
                    if len(findSize(i)):
                        if "Size" in myDict[prevHouse].keys():
                            myDict[prevHouse]["Size"] = myDict[prevHouse]["Size"]+ list(findSize(i))
                        else:
                            myDict[prevHouse]["Size"] = list(findSize(i))

                    if len(findFurntiure(i)):
                        myDict[prevHouse]["Furniture"] = findFurntiure(i)
                else:
                    if "Others" in myDict[prevHouse].keys():
                        myDict[prevHouse]["Others"].append(i)
                    else:
                        myDict[prevHouse]["Others"] = [i]
    return myDict, start_index+j

def filterSize(mydict):

    if "Rooms" in mydict.keys():
        mydict["Rooms"] = [ x.upper() for x in mydict["Rooms"] ]
        filterRooms(mydict)


def get_data_from_msg(string):

    lines  = string.split("\n")
    start_index =0
    end_index = 0
    i=0
    owner = "93280 59281"
    new_dic = dict()
    while i < len(lines):
        json_index = findALlRequiremnts(lines,i)
        print("json_index",json_index)
        print(i)
        if findOwner(lines[i])[0]:
            owner = findOwner(lines[i])[1]
            print("owner",owner)
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
            new_dic[owner].append(json_index[0])
            i =i+1

    #print("new_dic",new_dic)
    jsonlist = dict()

    prev_json = dict()
    for i in new_dic.keys():
        for j in  range(0, len(new_dic[i])):
            #print(new_dic[i][j])
            for k in new_dic[i][j].keys():
                filterSize(new_dic[i][j][k])
                present_json = new_dic[i][j][k]
                print("present_json",present_json)
                if "Newquery" in present_json.keys() and "endquery" not in present_json.keys():
                    prev_json = present_json

                if "endquery" in prev_json.keys():
                    prev_json = present_json

                if len(prev_json.keys()) and prev_json != present_json:
                    for key in prev_json.keys():
                        if not key in new_dic[i][j][k]:
                            if key in ["Type","PropertyType","Mobile","Budget","Society","Others"]:
                                new_dic[i][j][k][key] = prev_json[key]
                            elif key == "Size" and (("Rooms" not in prev_json.keys()  or len(prev_json["Rooms"]) == 0 ) or ("Rooms"  in present_json.keys()  and len(present_json["Rooms"]) == 0 )or "Rooms" not in present_json.keys() ):
                                new_dic[i][j][k][key] = prev_json[key]

                            elif key == "Area" and (("PropertyType" in prev_json.keys() or "PropertyType" in present_json.keys() ) or ("Newquery" in prev_json.keys()) or len(prev_json.keys())==1):
                                new_dic[i][j][k][key] = prev_json[key]

                            elif key in ["Rooms","Furniture"] and (("PropertyType" in present_json.keys() and present_json["PropertyType"][0] not in ["PLOT"]) or ("PropertyType" not in present_json.keys()) ):
                                new_dic[i][j][k][key] = prev_json[key]
                        
                        else:
                            if prev_json[key] != present_json[key]:
                                new_dic[i][j][k][key] = list(set(prev_json[key]+present_json[key]))
                
                
                
                prev_json  = new_dic[i][j][k]
                print("prev_json",prev_json)
                if i in jsonlist.keys():
                    jsonlist[i].append(prev_json)
                else:
                    jsonlist[i] = [prev_json]

    print(jsonlist)
    validlist = dict()
    for key in jsonlist.keys():
        for i,jobject in enumerate(jsonlist[key]):
            if "endquery" in jobject.keys():
                if "Mobile" in jsonlist[key][i-1].keys():
                        jsonlist[key][i-1]["Mobile"] = jsonlist[key][i-1]["Mobile"] + jsonlist[key][i]["Mobile"]
                else:
                    jsonlist[key][i-1]["Mobile"] = jsonlist[key][i]["Mobile"]
                if key in validlist.keys():
                    validlist[key].append(jsonlist[key][i-1])
                else:
                    validlist[key] = [jsonlist[key][i-1]]
            



    json_object = json.dumps(validlist, sort_keys=True, indent = 4) 
    
    with open("samplequery2.json", "w") as outfile:
        outfile.write(json_object)

    return validlist

#print(jsonlist)

