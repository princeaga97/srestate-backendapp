import imp
from random import random
from re import M
from time import monotonic
from venv import create
from django.contrib.auth import authenticate
from UserManagement.serializers import User
from rest_framework import serializers
from UserManagement.models import BrokersUsers ,User
from srestate.settings import TWILIO_AUTH_TOKEN ,TWILIO_ACCOUNT_SID
from twilio.rest import Client
import random
import uuid
from datetime import datetime



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

def send_otp(mobile):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    OTP = str(random.randint(100000,999999))
    print(OTP)
    message = client.messages \
                    .create(
                        body=f"OTP for SR ESTATE {OTP}",
                        from_='+18645288237',
                        to=f'+91{mobile}'
                    )
    print(message.sid)
    return OTP


def get_and_authenticate_user(Mobile, otp):
    user = authenticate(Mobile=Mobile, otp=otp)
    return user

def create_user_account(Mobile):
    #otp =send_otp(mobile = Mobile)
    otp = 123456
    brokeruser ,created = BrokersUsers.objects.get_or_create(
        Mobile=Mobile)
    brokeruser.otp = otp
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