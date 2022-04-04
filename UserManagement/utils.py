from random import random
from time import monotonic
from django.contrib.auth import authenticate
from UserManagement.serializers import User
from rest_framework import serializers
from UserManagement.models import Users
from srestate.settings import TWILIO_AUTH_TOKEN ,TWILIO_ACCOUNT_SID
from twilio.rest import Client
import random



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
    otp =send_otp(mobile = Mobile)
    #otp = 123456
    user, created = Users.objects.get_or_create(
        Mobile=Mobile, 
        is_broker = True)
    user.otp = otp
    if created:
        user.pk = len(Users.objects.all())+1
    user.save()
    Users.objects.filter(id=0).delete()
    return user ,created