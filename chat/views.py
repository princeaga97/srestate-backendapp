import re
import asyncio
from asgiref.sync import async_to_sync
from django.shortcuts import render
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, UpdateAPIView)
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from property.location.location_views import db
from django.http import JsonResponse
from property.estate.wputils import get_data_from_msg
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.decorators import renderer_classes, api_view 
from UserManagement.utils import send_sms ,send_whatsapp_msg   ,find_related_db
from chat.models import Messages,Contacts
from chat.serializers import MessageSerializer ,MessageViewSerializer , ContactViewSerializer
from property.utils import ReturnResponse ,create_msg , ReturnJsonResponse
from datetime import datetime
from django.db.models import Q
import json
import websockets
import requests
from property.location.location_views import db


# Create your views here.
# Create your views here.
def send_ws(WS_String,From,message):
    try:
        timeout = 5
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)              
        ws_conn = loop.run_until_complete(websockets.connect(WS_String))               
        loop.run_until_complete(ws_conn.send(json.dumps({"message":message,"sender":From,"sent":False})))
        loop.run_until_complete(ws_conn.close())
        return True
    except Exception as e:
        print("websocket Error " ,e)

def create_msg_in_db(data,sender,recieved = False):
    serilizer = MessageSerializer(data=data)
    if serilizer.is_valid():
        if recieved:
            contact_send,created = Contacts.objects.get_or_create(
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
    serializer_class = ContactViewSerializer
    def get_queryset(self) :
        request = self.request
        queryset = Contacts.objects.filter(Q(owner= request.user.mobile) & ~Q(contact = request.user.mobile) )
        return queryset
        

@api_view(('GET',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def get_contact_detail_view(request,broker,client) :
    queryset = Contacts.objects.filter(owner= broker ,contact = client).first()
    print(queryset)
    serializer = ContactViewSerializer( queryset , context={'request': request})
    mycol = db.property_estate
    findQuery ={}
    estate_list = serializer.data["eststate_list"].split(",")
    find_list = []
    for x in estate_list :
        find_list.append(int(x))
    findQuery["id"] = {"$in":find_list}
    print(list(mycol.find(findQuery)))
    data = serializer.data
    for index,estate in list(mycol.find(findQuery)):
        print("index",index)
        list(mycol.find(findQuery))[index].pop("_id")
        
    data["eststate_list"] =  list(mycol.find(findQuery))
    return ReturnJsonResponse(data =data ,success=True,msg="fetch successfully", status=status.HTTP_200_OK)


@api_view(('GET',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def chatByMobile(request):
    try:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        mobile = request.GET.get('mobile')
        print(request.user)
        if mobile is None:
            return ReturnJsonResponse(errors=["please enter mobile"],success=False,msg="Invalid Request", status=status.HTTP_400_BAD_REQUEST)
        chats = Messages.objects.filter(
                Q(sender_name=request.user.mobile, receiver_name = mobile )|
                    Q(receiver_name=request.user.mobile, sender_name = mobile )
            )
        result_page = paginator.paginate_queryset(chats, request)
        if chats:
            serializer = MessageViewSerializer(chats,many = True , context={'request': request})
            return ReturnJsonResponse(data =serializer.data ,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        else:
            return ReturnJsonResponse(data = [],success=True,msg="PLease Send First Message", status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return ReturnJsonResponse(errors=str(e),success=False,msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        WS_String  = f"wss://srestatechat.herokuapp.com/ws/chat/{sender}_{From}/"
        print(WS_String)# Once the task is created, it will begin running in parallel
        send_ws(WS_String,From,request.POST["Body"])
        
        message, sucess = create_msg_in_db(data,From,recieved=True)
        
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
                print(send_whatsapp_msg(From,messageString))
                data = {
                    "description":messageString[0],
                    "receiver_name":From,
                    "seen":False
                }
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
