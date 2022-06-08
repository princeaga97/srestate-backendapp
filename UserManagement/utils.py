from random import random
from venv import create
from django.contrib.auth import authenticate
from UserManagement.serializers import User
from rest_framework import serializers
from UserManagement.models import BrokersUsers ,User
from srestate.settings import TWILIO_AUTH_TOKEN ,TWILIO_ACCOUNT_SID
from twilio.rest import Client
import random
from datetime import datetime



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

def read_json_related(findQuery):
    budget=0 
    floor_space =0
    number_of_bedrooms =0
    estate_status = ""
    if "estate_type" in findQuery.keys():
        estate_type = findQuery["estate_type"]
        if not isinstance(estate_type,list):
            findQuery["estate_type"] = [estate_type]
    if "area" in findQuery.keys():
        area = findQuery["area"]
        if not isinstance(area,list):
            findQuery["area"] = [area]
    else:
        findQuery["area"] = []
    if "estate_status" in findQuery.keys():
        if isinstance(findQuery["estate_status"],list):
            findQuery["estate_status"] = findQuery["estate_status"][0]
        if findQuery["estate_status"] == "sell":
            estate_status = "purchase"
        elif findQuery["estate_status"] == "purchase":
            estate_status = "sell"
        elif findQuery["estate_status"] == "rent":
            estate_status = "rent" 
    if "budget" in findQuery.keys():
        budget = findQuery["budget"]
        if isinstance(budget,list):
            budget.sort()
            budget = budget[-1]
        budget = float(budget) + 0.1* float(budget)
    if "floor_space" in findQuery.keys():
        floor_space = findQuery["floor_space"]
        if isinstance(floor_space,list):
            floor_space.sort()
            floor_space = floor_space[-1]
        floor_space = float(floor_space) + 0.1* float(floor_space)
    if "number_of_bedrooms" in findQuery.keys():
        number_of_bedrooms = findQuery["number_of_bedrooms"]

    return findQuery,number_of_bedrooms,budget,floor_space,estate_status


def find_related_db(mycol,findQuery):
    budget=0 
    floor_space =0
    findQuery,number_of_bedrooms,budget,floor_space,estate_status = read_json_related(findQuery)
    
    print(findQuery,number_of_bedrooms,budget,floor_space,estate_status)

    if "flat" not in findQuery["estate_type"]:
        
        queryset= mycol.aggregate([
            {
                "$match" : { "$and": [ 
                    {"$and": [{ "id": {"$ne":findQuery["id"]} },{ "estate_status": estate_status },{ "broker_mobile": findQuery["broker_mobile"] }]},
                    {"$or": [
                      {"$or" : [ { "area": {"$in" :findQuery["area"] }}]},
                      {"$or" :[{ "estate_type": {"$in" :findQuery["estate_type"] }}]},
                      {"$or" : [ { "floor_space": {"$lte": floor_space } }]},
                      {"$or" :[{ "budget": {"$lte": budget } }]}
                    ]}
                ]} } ]
            )
    else:
        queryset= mycol.aggregate([
            {
                "$match" : { "$and": [ 
                    {"$and": [{ "id": {"$ne":findQuery["id"]} },{ "estate_status": estate_status },{ "number_of_bedrooms":{"$in" :number_of_bedrooms }},{ "broker_mobile": findQuery["broker_mobile"] }]},
                    {"$or": [
                      {"$or" : [ { "area": {"$in" :findQuery["area"] }}]},
                      {"$or" :[{ "estate_type": {"$in" :findQuery["estate_type"] }}]},
                      {"$or" : [ { "floor_space": {"$lte": floor_space } }]},
                      {"$or" :[{ "budget": {"$lte": budget } }]}
                    ]}
                ]} } ]
            )
    return queryset

def send_whatsapp_msg(mobile,messageString):
    try:
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token) 
        
        message = client.messages.create( 
                                    from_='whatsapp:+14155238886',  
                                    body=messageString,
                                    to=f'whatsapp:+91{mobile}' 
                                ) 
        
        print(message.sid)
        msg_status= {}
        msg_status["success"] = True
        msg_status["msg"] = "Success"
        return msg_status
    except Exception as e:
        msg_status= {}
        msg_status["success"] = False
        msg_status["msg"] = str(e)
        return msg_status



def send_otp(mobile, appString):
    try:
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        OTP = str(random.randint(100000,999999))
        print(OTP)
        message = client.messages \
                        .create(
                            body=f"  {appString} SR ESTATE  for {OTP} OTP for Verification",
                            from_='+19785772148',
                            to=f'+91{mobile}'
                        )
        print(message.sid)
        return OTP
    except Exception as e:
        print(e)
        return 123456

def send_sms(mobile,messageString):
    try:
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages \
                        .create(
                            body=messageString,
                            from_='+18645288237',
                            to=f'+91{mobile}'
                        )
        print(message.sid)
        msg_status= {}
        msg_status["success"] = True
        msg_status["msg"] = "Success"
        return msg_status
    except Exception as e:
        msg_status= {}
        msg_status["success"] = False
        msg_status["msg"] = str(e)
        return msg_status



def get_and_authenticate_user(Mobile, otp):
    user = authenticate(Mobile=Mobile, otp=otp)
    return user

def create_user_account(Mobile,appString):
    otp =send_otp(mobile = Mobile, appString=appString)
    #otp = 123456
    brokeruser ,created = BrokersUsers.objects.get_or_create(
        Mobile=Mobile)
    brokeruser.otp = otp
    brokeruser.balance = 1000
    brokeruser.save()
    print(created)
    if created == True:
        user = User.objects.create(
            username = str(Mobile),
            password = str(otp*2),
            is_superuser = False,
            first_name = " ",
            last_name = " ",
            mobile = Mobile,
            is_active = True,
            last_login = datetime.now(),

        )
    else:
        user = User.objects.get(mobile = Mobile)
    return user , created