from curses import keyname
from email.policy import HTTP
from pydoc import cli
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from tabnanny import check
from rest_framework.generics import ListAPIView ,CreateAPIView,DestroyAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser ,JSONParser
from rest_framework.decorators import api_view ,authentication_classes, permission_classes ,parser_classes
import json
from srestate.settings import mongo_uri , CACHES
from property.estate.wputils import get_data_from_msg
from django.views.decorators.csrf import csrf_exempt
from property.estate.estate_serializers import EstateSerializer, EstateStatusSerializer, EstateTypeSerializer,ImageSerializer , EstateWPSerializer
from property.models import Estate, EstateStatus, EstateType ,photos,City,Apartment,Area , Broker
import pymongo
import redis
from property.utils import create_msg , check_balance
from property.location.location_views import db
from UserManagement.utils import send_sms ,send_whatsapp_msg 



cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])



def modify_input_for_multiple_files(estate_id, image):
    dict = {}
    dict['estate_id'] = estate_id
    dict['image'] = image
    return dict



@api_view(('POST',))
@permission_classes([])
@parser_classes([JSONParser,])
@csrf_exempt
def get_data_from_wp(request):
    serializer = EstateWPSerializer(data= json.loads(request.body))
    if serializer.is_valid():
        data = get_data_from_msg(**serializer.data)
        
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
@csrf_exempt
def get_buy_estate(request):
    mycol = db.property_estate
    print(request.user)
    queryset= mycol.find({
        "broker_mobile":request.user.mobile,
        "estate_type":"buy"
        })
    cache_query = str(request.user.mobile) + "buy"
    if cache_query in cache:
        estates = cache.get(cache_query)
        estates = json.loads(estates)
        if queryset.count()!= len(estates):
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name = request.user.mobile, value=jobject, time=60*15)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(estates, status=status.HTTP_200_OK)
    else:
        serializer = EstateSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= cache_query, value=jobject, time=60*15)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(('GET',))
@csrf_exempt
def get_sell_estate(request):
    mycol = db.property_estate
    queryset= mycol.find({
        "broker_mobile":request.user.mobile,
        "estate_type":"sell"
        })
    cache_query = str(request.user.mobile) + "sell"
    if cache_query in cache:
        estates = cache.get(cache_query)
        estates = json.loads(estates)
        if queryset.count()!= len(estates):
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name = request.user.mobile, value=jobject, time=60*15)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(estates, status=status.HTTP_200_OK)
    else:
        serializer = EstateSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= cache_query, value=jobject, time=60*15)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@csrf_exempt
def get_filter_estate(request):

    findQuery = {}
    findQuery["broker_mobile"] = request.user.mobile
    if "area" in request.data.keys() and list(request.data["area"]):
        findQuery["area"] = {"$in":list(request.data["area"])}
    
    if "estate_status" in request.data.keys() and list(request.data["estate_status"]):
        findQuery["estate_status"] = {"$in":list(request.data["estate_status"])}
    
    if "estate_type" in request.data.keys() and list(request.data["estate_type"]):
        findQuery["estate_type"] = {"$in":list(request.data["estate_type"])}
    
    if "number_of_bedrooms" in request.data.keys() and list(request.data["number_of_bedrooms"]):
        findQuery["number_of_bedrooms"] = {"$in":list(request.data["number_of_bedrooms"])}
    
    if "society" in request.data.keys() and list(request.data["apartment"]):
        findQuery["society"] = {"$in":list(request.data["apartment"])}
    
    if "budget" in request.data.keys() and list(request.data["budget"]):

        findQuery["budget"] = {"$gte":list(request.data["budget"])[0],"$lte":list(request.data["budget"])[1]}
    

    mycol = db.property_estate
    queryset= mycol.find(findQuery)
    cache_query = str(request.user.mobile) + "sell"
    if cache_query in cache:
        estates = cache.get(cache_query)
        estates = json.loads(estates)
        if queryset.count()!= len(estates):
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name = request.user.mobile, value=jobject, time=60*15)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(estates, status=status.HTTP_200_OK)
    else:
        serializer = EstateSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= cache_query, value=jobject, time=60*15)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

@api_view(('POST',))
@csrf_exempt
def send_message(request):
    findQuery ={}
    if "estates" in request.data.keys() and list(request.data["estates"]):
        findQuery["id"] = {"$in":list(request.data["estates"])}
    findQuery["broker_mobile"] = request.user.mobile
    
    print(findQuery)
    mycol = db.property_estate
    queryset= mycol.find({})
    response ={"success":True,
        "error":" "}
    if queryset:
        listestate = list(queryset)
        messageString = create_msg(listestate)
        if messageString[0] == "":
            return Response(data=response, status=status.HTTP_200_OK)
        if request.user.balance < check_balance(request,listestate):
            response["success"] =False
            response["error"] = "Insufficent Balance"
            response["required_balance"] = check_balance(request,listestate)
            response["balance"] = request.user.balance
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        mobile_number = request.data["mobile"]
        
        # if "sms" in request.data and  request.data["sms"]:
        #     sms = send_sms(mobile_number,messageString[0])
        #     response["sms"] = sms
        #     if not sms["success"]:
        #         response["error"] = "sms failed"
        #         response["success"] = False
        #     else:
        #         request.user.balance = request.user.balance - len(listestate)*5
        #         request.user.save()
        # if "whatsapp" in request.data and  request.data["whatsapp"]:
        #     whatsapp = send_whatsapp_msg(mobile_number,messageString[0])
        #     response["whatsapp"] = whatsapp
        #     if not whatsapp["success"]:
        #         response["error"] =response["error"] + "sms failed"
        #         response["success"] = False
        #     else:
        #         request.user.balance = request.user.balance - len(listestate)*10
        #         request.user.save()
           
        if response["success"]:
            query = db.property_enquiryquerys
            query.insert_one(messageString[1])
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)







@permission_classes([])
class ListEstateAPIView(ListAPIView):
    serializer_class = EstateSerializer
    def get(self,request):
        
        mycol = db.property_estate
        queryset= mycol.find({"broker_mobile":request.user.mobile})
        
        
        if request.user.mobile in cache:
            estates = cache.get(request.user.mobile)
            estates = json.loads(estates)
            if queryset.count()!= len(estates):
                serializer = EstateSerializer(queryset,many = True)
                jobject = json.dumps(serializer.data)
                cache.setex(name = request.user.mobile, value=jobject, time=60*15)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(estates, status=status.HTTP_200_OK)
        else:
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name= request.user.mobile, value=jobject, time=60*15)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

@permission_classes([])
class CreateEstateAPIView(CreateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

    def post(self,request,mobile):
        serilizer = EstateSerializer(data=request.data)
        
        if serilizer.is_valid():
            if len(str(mobile)) == 10:
                broker,created = Broker.objects.get_or_create(
                name = serilizer.data["broker_name"],
                mobile = int(mobile)
                )
                print(request.data)
            data1 =  serilizer.validated_data
            # converts querydict to original dict
            flag = 1
            arr = []
            if "Images" in data1:
                data1.pop("Images")
                images = dict((request.data).lists())['Images']
                for img_name in images:
                    print(img_name)
                    modified_data = modify_input_for_multiple_files(estate.id,
                                                                    img_name)
                    file_serializer = ImageSerializer(data=modified_data)
                    if file_serializer.is_valid():
                        image = file_serializer.create(file_serializer.validated_data)
                        arr.append(image.estate_id.id)
                    else:
                        print(file_serializer.errors)
                        flag = 0
            

            if data1["city"] is not None:
                city,created = City.objects.get_or_create(
                city_name = serilizer.data["city"].lower()
            )

            if data1["estate_type"] is not None:
                estate_type,created = EstateType.objects.get_or_create(
                type_name = serilizer.data["estate_type"].lower()
            )

            if data1["estate_status"] is not None:
                estate_status,created = EstateStatus.objects.get_or_create(
                estate_status_name = serilizer.data["estate_status"].lower()
            )

            if data1["area"] is not None:
                area,created = Area.objects.get_or_create(
                area_name = serilizer.data["area"].lower()
            )

            if data1["society"] is not None:
                society,created = Apartment.objects.get_or_create(
                apartment_name = serilizer.data["society"].lower(),
                area = serilizer.data["area"].lower()
            )



            for i in data1.keys():
                if type(data1[i]) == str:
                    data1[i] = data1[i].lower()

            estate = serilizer.create(data1)
            print(estate)
            estate.broker_mobile = mobile
            estate.save()
            if flag == 1:
                context = {
                    "images":arr,
                    "msg":"Created Successfully and Images Saved"
                }

            else:
                context = {
                    "images": arr,
                    "msg": "Created Successfully"
                }

            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class UpdateEstateAPIView(UpdateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class DeleteEstateAPIView(DestroyAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer


class ListEstateStatusAPIView(ListAPIView):
    queryset = EstateStatus.objects.filter(is_deleted = 0)
    serializer_class = EstateStatusSerializer
    def get(self,request):
        mycol = db.property_estatestatus
        queryset = mycol.find({"is_deleted":False})
        if "estate_status" in cache:
            estate_status = cache.get("estate_status")
            estate_status = json.loads(estate_status)
            if queryset.count()!= len(estate_status):
                serializer = EstateStatusSerializer(queryset,many = True)
                print(serializer)
                jobject = json.dumps(serializer.data)
                cache.setex(name = "estate_status", value=jobject, time=60*60)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(estate_status, status=status.HTTP_200_OK)
        serializer = EstateStatusSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= "estate_status", value=jobject, time=60*60)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class CreateEstateStatusAPIView(CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer

    def post(self,request):
        serilizer = EstateStatusSerializer(data=request.data)

        if serilizer.is_valid():
            estate_status,created = EstateStatus.objects.get_or_create(
                estate_status_name = serilizer.data["estate_status_name"]
            )
            estate_status.save()

            context = {
                "msg":"Created Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)



class UpdateEstateStatusAPIView(UpdateAPIView):
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer
    def put(self,request,**kwargs):
        serilizer = EstateStatusSerializer(data=request.data)
        id = kwargs.get('pk',0)
        if serilizer.is_valid():
            try:
                estate_status = EstateStatus.objects.get(pk = id)
                estate_status.estate_status_name = serilizer.data["estate_status_name"]
                estate_status.save()

                context = {
                    "msg":"Updated Successfully"
                }

                return Response(context, status=status.HTTP_200_OK)

            except EstateStatus.DoesNotExist:
                context = {
                    "msg": "Record Does Not Exists"
                }

                return Response(context, status=status.HTTP_200_OK)


        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class DeleteEstateStatusAPIView(DestroyAPIView):
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk',0)
        try:
            estate_status = EstateStatus.objects.get(pk = id)
            estate_status.is_deleted = True
            estate_status.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except EstateStatus.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)







class ListEstateTypeAPIView(ListAPIView):
    queryset = EstateType.objects.filter(is_deleted = 0)
    serializer_class = EstateTypeSerializer
    def get(self,request):
        mycol = db.property_estatetype
        queryset = mycol.find({"is_deleted":False})
        if "estate_type" in cache:
            estate_types = cache.get("estate_type")
            estate_types = json.loads(estate_types)
            if queryset.count()!= len(estate_types):
                serializer = EstateTypeSerializer(queryset,many = True)
                print(serializer)
                jobject = json.dumps(serializer.data)
                cache.setex(name = "estate_type", value=jobject, time=60*60)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(estate_types, status=status.HTTP_200_OK)
        serializer = EstateTypeSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= "estate_type", value=jobject, time=60*60)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



class CreateEstateTypeAPIView(CreateAPIView):
    queryset = EstateType.objects.all()
    serializer_class = EstateTypeSerializer

    def post(self,request):
        serilizer = EstateTypeSerializer(data=request.data)

        if serilizer.is_valid():
            estate_type,created = EstateType.objects.get_or_create(
                type_name = serilizer.data["type_name"]
            )
            estate_type.save()

            context = {
                "msg":"Created Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UpdateEstateTypeAPIView(UpdateAPIView):
    queryset = EstateType.objects.all()
    serializer_class = EstateTypeSerializer
    def put(self,request,**kwargs):
        serilizer = EstateTypeSerializer(data=request.data)
        id = kwargs.get('pk',0)
        if serilizer.is_valid():
            try:
                estate_type = EstateType.objects.get(pk = id)
                estate_type.type_name = serilizer.data["type_name"]
                estate_type.save()

                context = {
                    "msg":"Updated Successfully"
                }

                return Response(context, status=status.HTTP_200_OK)

            except EstateType.DoesNotExist:
                context = {
                    "msg": "Record Does Not Exists"
                }

                return Response(context, status=status.HTTP_200_OK)

        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_201_CREATED)

class DeleteEstateTypeAPIView(DestroyAPIView):
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk','0')
        try:
            estate_type = EstateType.objects.get(pk = id)
            estate_type.is_deleted = 1
            estate_type.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except EstateType.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)





