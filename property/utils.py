import uuid
from rest_framework.response import Response
from rest_framework import status
from property.message_mapping import MSG_MAPPING ,QUERY_MAPPING
import json
from django.http import JsonResponse

def check_balance(request,listestate):
    amount  = 0

    if "sms" in request.data and  request.data["sms"]:
        amount = amount +  5 * len(listestate)
    if "whatsapp" in request.data and  request.data["whatsapp"]:
        amount = amount +  10 * len(listestate)
    
    return amount

def create_msg(jobject):
    msg_string = ""
    query_json =      {
            "type" :[],
            "estate_type" :[],
            "budget" :[],
            "area" :[]
            }
    for estate in jobject:
        msg_string = msg_string + " \n \n" + str(estate["estate_name"]).upper()
        
        for attribute, value in estate.items():
            if attribute in MSG_MAPPING.keys():
                msg_string = msg_string + " \n" + MSG_MAPPING[attribute] + " " + str(value)
            if attribute in QUERY_MAPPING.keys():
                query_json[QUERY_MAPPING[attribute]].append(value)
        
        for key in query_json.keys():
            query_json[key] = list(set(query_json[key]))
        query_json["id"] = str(uuid.uuid4())
    return msg_string,query_json


def ReturnResponse(status,errors=[],data=[],msg="",success=False):
    response = {

        "success":success,
        "error":errors,
        "message":msg,
        "data":data,
    }
    return Response(data= response,status = status)


def ReturnJsonResponse(status,errors=[],data=[],msg="",success=False):
    if type(data) == str:
        data = json.loads(data)
    response = {

        "success":success,
        "error":errors,
        "message":msg,
        "data":data,
    }
    return JsonResponse(data= response,status = status)

