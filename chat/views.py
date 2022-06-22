import re
from django.shortcuts import render
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, UpdateAPIView)
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from property.location.location_views import db
from django.http import JsonResponse
from property.estate.wputils import get_data_from_msg
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.decorators import renderer_classes
from UserManagement.utils import send_sms ,send_whatsapp_msg  , read_json_related ,find_related_db
from chat.models import Messages,Contacts
from chat.serializers import MessageSerializer ,MessageViewSerializer , ContactViewSerializer
from property.utils import ReturnResponse ,create_msg
from datetime import datetime


# Create your views here.
# Create your views here.

def create_msg_in_db(data,sender,recieved = False):
    serilizer = MessageSerializer(data=data)
    if serilizer.is_valid():
         

        if recieved:
            contact_send, created = Contacts.objects.get_or_create(
                contact = sender,
                owner = serilizer.validated_data["receiver_name"]
            )
            serilizer.validated_data["sender_name"] = sender
            serilizer.validated_data["sent"] = False
            message = serilizer.create(serilizer.validated_data)
        else:
            contact_send, created = Contacts.objects.get_or_create(
                owner = sender,
                contact  = serilizer.validated_data["receiver_name"]
            )
            print("data",data)
            serilizer.validated_data["sender_name"] = sender
            serilizer.validated_data["sent"] = True
            message = serilizer.create(serilizer.validated_data)

        contact_send.last_message = message
        contact_send.timestamp = datetime.now()
        contact_send.save()
        return message,True
    else:
        return serilizer.errors,False


class ListMessageAPIView(ListAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageViewSerializer

class CreateMessageAPIView(CreateAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer

    def post(self,request):
        send_whatsapp_msg(request.data["receiver_name"],request.data["description"])
        message, sucess = create_msg_in_db(request.data,request.user.mobile)
        if sucess:
            return ReturnResponse(success=True, status=status.HTTP_200_OK)
        else:
            return ReturnResponse(success=False,errors= message, status=status.HTTP_400_BAD_REQUEST)


class ListContactAPIView(ListAPIView):
    queryset = Contacts.objects.all()
    serializer_class = ContactViewSerializer


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def demo_reply(request):
    From = request.POST["From"][12:]
    print(From)
    msg  = None
    if request.POST["Body"] is not None:
        sender_list = Contacts.objects.filter(contact = From).last()
        if sender_list:
            sender = sender_list.owner
        
        data = {
                "description":request.POST["Body"],
                "receiver_name":sender,
                "seen":False
            }
        message, sucess = create_msg_in_db(data,From,recieved=True)
        if request.POST["Body"].lower() == "hi":

            msg = "good effort"
            send_whatsapp_msg(From,msg)
            data = {
                "description":msg,
                "receiver_name":From,
                "seen":False
            }

            message, sucess = create_msg_in_db(data,sender)
            if sucess:
                return JsonResponse({ "success":True}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"success":False,"errors": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            out_json = get_data_from_msg(request.POST["Body"])
            if out_json:
                findQuery = out_json[list(out_json.keys())[0]][0]
                findQuery["broker_mobile"] = sender
                findQuery["id"] =0
                if "bhk" in request.POST["Body"] and "estate_type" not in findQuery:
                    findQuery["estate_type"] = ['flat']
                mycol = db.property_estate
                queryset = find_related_db(mycol,findQuery)
                if queryset:
                    listestate = list(queryset)
                    messageString = create_msg(listestate)
                    send_whatsapp_msg(From,messageString)
                    data = {
                        "description":messageString[0],
                        "receiver_name":From,
                        "seen":False
                    }
                    print("messageString",messageString[0])
                    message, sucess = create_msg_in_db(data,sender)
                else:
                    messageString = "no estate found"
                    send_whatsapp_msg(From,messageString)
                    data = {
                        "description":messageString,
                        "receiver_name":From,
                        "seen":False
                    }
                    message, sucess = create_msg_in_db(data,sender)

            else:
                messageString = "no qyery found"
                send_whatsapp_msg(From,messageString)
                data = {
                    "description":messageString,
                    "receiver_name":From,
                    "seen":False
                }

                message, sucess = create_msg_in_db(data,sender)
                    

        return JsonResponse({"data": messageString},status = status.HTTP_200_OK)

