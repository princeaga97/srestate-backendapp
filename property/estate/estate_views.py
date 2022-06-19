from email import message
from selectors import EpollSelector
from rest_framework.generics import ListAPIView ,CreateAPIView,DestroyAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.parsers import MultiPartParser,FormParser ,JSONParser
from rest_framework.decorators import api_view ,authentication_classes, permission_classes ,parser_classes ,renderer_classes
import json
from django.http import JsonResponse
from srestate.settings import mongo_uri , CACHES
from property.estate.wputils import get_data_from_msg
from django.views.decorators.csrf import csrf_exempt
from property.estate.estate_serializers import EstateSerializer, EstateStatusSerializer, EstateTypeSerializer,ImageSerializer , EstateWPSerializer
from property.models import Estate, EstateStatus, EstateType ,photos,City,Apartment,Area , Broker
import redis
from property.utils import create_msg , check_balance ,ReturnResponse
from property.location.location_views import db
from UserManagement.utils import send_sms ,send_whatsapp_msg  , read_json_related ,find_related_db



cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])



def modify_input_for_multiple_files(estate_id, image):
    dict = {}
    dict['estate_id'] = estate_id
    dict['image'] = image
    return dict


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def demo_reply(request):
    From = request.POST["From"][12:]
    print(From)
    if request.POST["Body"] is not None:
        if request.POST["Body"].lower() == "hi":
            send_whatsapp_msg(From,"good effort")
        # elif "bhk" in request.POST["Body"].lower():
        #     mycol = db.property_estate
        #     data = mycol.find({"number_of_bedrooms":int(request.POST["Body"][0])})
        #     if data:
        #         listestate = list(data)
        #         messageString = create_msg(listestate)
        #         send_whatsapp_msg(From,messageString)
        else:
            out_json = get_data_from_msg(request.POST["Body"])
            if out_json:
                findQuery = out_json[list(out_json.keys())[0]][0]
                print(findQuery)
                if "broker_mobile" in findQuery.keys() and findQuery["broker_mobile"]:
                    findQuery["broker_mobile"] = findQuery["broker_mobile"][0]
                findQuery["id"] =0
                if "bhk" in request.POST["Body"] and "estate_type" not in findQuery:
                    findQuery["estate_type"] = ['flat']
                mycol = db.property_estate
                queryset = find_related_db(mycol,findQuery)
                if queryset:
                    listestate = list(queryset)
                    messageString = create_msg(listestate)
                    send_whatsapp_msg(From,messageString)
    return JsonResponse({"data": messageString},status = status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes([])
@parser_classes([JSONParser,])
@csrf_exempt
def get_data_from_wp(request):
    try:
        serializer = EstateWPSerializer(data= json.loads(request.body))
        if serializer.is_valid():
            data = get_data_from_msg(**serializer.data)
            
            return ReturnResponse(data=data,success=True,msg="created sucessfully", status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return ReturnResponse(errors=serializer.errors,success=False,msg="invalid data", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ReturnResponse(errors=str(e),success=False,msg="Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(('GET',))
@csrf_exempt
def get_buy_estate(request):
    try:
        cache_query = str(request.user.mobile) + "buy"
        if cache_query in cache:
            estates = cache.get(cache_query)
            estates = json.loads(estates)
            return ReturnResponse(data = estates,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        else:
            mycol = db.property_estate
            print(request.user)
            queryset= mycol.find({
                "broker_mobile":request.user.mobile,
                "estate_status":"purchase"
                })
            if queryset.count() == 0:
                return ReturnResponse(data=[],success=True,msg="no data found", status=status.HTTP_200_OK)
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name= cache_query, value=jobject, time=60*15)
            return ReturnResponse(data = serializer.data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),success=False,msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(('GET',))
@csrf_exempt
def get_sell_estate(request):
    try:
        
        cache_query = str(request.user.mobile) + "sell"
        if cache_query in cache:
            estates = cache.get(cache_query)
            estates = json.loads(estates)
            data = estates
        else:
            mycol = db.property_estate
            queryset= mycol.find({
                "broker_mobile":request.user.mobile,
                "estate_status":"sell"
                })
            if queryset.count() == 0:
                return ReturnResponse(data=[],success=True,msg="no data found", status=status.HTTP_200_OK)
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name= cache_query, value=jobject, time=60*15)
            data = serializer.data
        return ReturnResponse(data = data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(('GET',))
@csrf_exempt
def get_filter_details(request):

    try:
        cache_query = "filter_details"
        if cache_query in cache:
            filter_details = cache.get(cache_query)
            filter_details = json.loads(filter_details)
            return ReturnResponse(data = filter_details,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        required_fields = {
        "area":[],
        "estate_status":[],
        "furniture":["fully furnished","semi furnished","luxurious furnished","furnished","renovated"],
        "estate_type":[],
        "budget" : [],
        "rooms" : []
        }

        mapping_db = {
            "area":["area_name",db.property_area.find({},{"area_name":1,"_id":0})],
            "estate_status":["estate_status_name",db.property_estatestatus.find({},{"estate_status_name":1,"_id":0})],
            "estate_type":["type_name",db.property_estatetype.find({},{"type_name":1,"_id":0})],
            "budget":["budget",db.property_estate.find({},{"budget":1,"_id":0})],
            "rooms" : ["number_of_bedrooms",db.property_estate.find({},{"number_of_bedrooms":1,"_id":0})],
            "floor_space" : ["floor_space",db.property_estate.find({},{"floor_space":1,"_id":0})]
        }
        
        
        for key,value  in mapping_db.items(): 
            if key not in ["budget","rooms","floor_space"]:
                required_fields[key] = [ x.get(value[0],"").lower() for x in   list(value[1]) ]
                # required_fields[key] = [ x  for x in   list(value[1]) if x!=""]
            else:
                if key =="budget":
                    required_fields[key] = [ float(str(x.get(value[0],0))) for x in   list(value[1]) ]
                else:
                    required_fields[key] = [ int(str(x.get(value[0],0))) for x in   list(value[1]) if x > 0]
                    
                required_fields[key].sort()
                required_fields[key] = list(set(required_fields[key]))
                if key != "rooms":
                    required_fields[key] = [required_fields[key][0],required_fields[key][-1]]
            
        jobject = json.dumps(required_fields)
        cache.setex(name= cache_query, value=jobject, time=60*60*24)
        return ReturnResponse(data=required_fields,msg="",success=True, status=status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(('POST',))
@csrf_exempt
def get_filter_estate(request):

    try:
        findQuery = {}
        findQuery["broker_mobile"] = request.user.mobile
        filter_paramneters = ["area", "estate_status" , "estate_type" , "number_of_bedrooms" , "society" ,"furniture" , "budget"]

        for parameter in filter_paramneters:
            if parameter in request.data.keys() and list(request.data[parameter]):
                if len(list(request.data[parameter])):
                    findQuery[parameter] = {"$in":list(request.data[parameter])}
        
        if "budget" in request.data.keys() and list(request.data["budget"]):
            findQuery["budget"] = {"$gte":min(list(request.data["budget"])),"$lte":max(list(request.data["budget"]))}
        
        if "floor_space" in request.data.keys() and list(request.data["floor_space"]):
            findQuery["floor_space"] = {"$gte":min(list(request.data["floor_space"])),"$lte":max(list(request.data["floor_space"]))}
        
        mycol = db.property_estate
        queryset= mycol.find(findQuery)
        serializer = EstateSerializer(queryset,many = True)
        return ReturnResponse(data=serializer.data,success=True, msg= "fetch successfully", status=status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(('POST',))
@csrf_exempt
def send_message(request):
    try:
        findQuery ={}
        if "estates" in request.data.keys() and list(request.data["estates"]):
            findQuery["id"] = {"$in":list(request.data["estates"])}
        findQuery["broker_mobile"] = request.user.mobile
        
        print(findQuery)
        mycol = db.property_estate
        queryset= mycol.find(findQuery)
        response ={"success":True,
            "error":" "}
        if queryset:
            listestate = list(queryset)
            messageString = create_msg(listestate)
            if messageString[0] == "":
                return ReturnResponse(success=False,msg="no data found",status= status.HTTP_200_OK)
            if request.user.balance < check_balance(request,listestate):
                response["required_balance"] = check_balance(request,listestate)
                response["balance"] = request.user.balance
                return ReturnResponse(data=response, errors=["Insufficent Balance"],success=False,msg="no data found",status= status.HTTP_200_OK)

            mobile_number = request.data["mobile"]
            
            if "sms" in request.data and  request.data["sms"]:
                sms = send_sms(mobile_number,messageString[0])
                response["sms"] = sms
                if not sms["success"]:
                    response["error"] = "sms failed"
                    response["success"] = False
                else:
                    request.user.balance = request.user.balance - len(listestate)*5
                    request.user.save()
            if "whatsapp" in request.data and  request.data["whatsapp"]:
                whatsapp = send_whatsapp_msg(mobile_number,messageString[0])
                response["whatsapp"] = whatsapp
                if not whatsapp["success"]:
                    response["error"] =response["error"] + "sms failed"
                    response["success"] = False
                else:
                    request.user.balance = request.user.balance - len(listestate)*10
                    request.user.save()
            
            if response["success"]:
                query = db.property_enquiryquerys
                query.insert_one(messageString[1])
                return ReturnResponse(data=response,success=True,msg="message sent successfully",status= status.HTTP_200_OK)
            else:
                return ReturnResponse(errors=response,success=True,msg="message sent successfully",status= status.HTTP_200_OK)
        else:
            return ReturnResponse(success=True,msg="no data found",status= status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@permission_classes([])
class ListEstateAPIView(ListAPIView):
    serializer_class = EstateSerializer
    def get(self,request):
        try:
            if request.user.mobile in cache:
                estates = cache.get(request.user.mobile)
                estates = json.loads(estates)
                data = estates
                
            else:
                mycol = db.property_estate
                queryset= mycol.find({"broker_mobile":request.user.mobile}) 
                if queryset.count() == 0:
                    return ReturnResponse(data=[],success=True,msg="no data found", status=status.HTTP_200_OK)
                serializer = EstateSerializer(queryset,many = True)
                jobject = json.dumps(serializer.data)
                cache.setex(name= request.user.mobile, value=jobject, time=60*15)
                data = serializer.data
                print(data)
            return ReturnResponse(data = data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class CreateEstateAPIView(CreateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

    def post(self,request):

        try:

            cache.delete(str(request.user.mobile) + "buy")
            cache.delete(str(request.user.mobile) + "sell")
            cache.delete(str(request.user.mobile))
            serializer = EstateSerializer(data=request.data)
            mobile = request.user.mobile
            if serializer.is_valid():
                if len(str(mobile)) == 10:
                    broker,created = Broker.objects.get_or_create(
                    mobile = int(mobile)
                    )
                    print(request.data)
                data1 =  serializer.validated_data
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
                    city_name = serializer.data["city"].lower()
                )

                if data1["estate_type"] is not None:
                    estate_type,created = EstateType.objects.get_or_create(
                    type_name = serializer.data["estate_type"].lower()
                )

                if data1["estate_status"] is not None:
                    estate_status,created = EstateStatus.objects.get_or_create(
                    estate_status_name = serializer.data["estate_status"].lower()
                )

                if data1["area"] is not None:
                    area,created = Area.objects.get_or_create(
                    area_name = serializer.data["area"].lower()
                )

                if data1["society"] is not None:
                    society,created = Apartment.objects.get_or_create(
                    apartment_name = serializer.data["society"].lower(),
                    area = serializer.data["area"].lower()
                )



                for i in data1.keys():
                    if data1[i].isdigit():
                        data1[i] = int(data1[i])
                    elif type(data1[i]) == str:
                        data1[i] = data1[i].lower()
                    
                    

                estate = serializer.create(data1)
                print(estate)
                estate.broker_mobile = mobile
                estate.broker_name = broker.name
                estate.save()
                try:
                    mycol = db.property_estate
                    queryset= mycol.find({
                        "broker_mobile":request.user.mobile,
                        })
                    if len(queryset):
                        serializer = EstateSerializer(queryset,many = True)
                        jobject = json.dumps(serializer.data)
                        cache.setex(name= request.user.mobile, value=jobject, time=60*15)

                    estate_sell =  [ _estate_ for _estate_ in list(queryset) if _estate_["estate_status"] == "sell" ]
                    jobject = json.dumps(estate_sell)
                    if len(estate_sell):
                        cache.setex(name= str(request.user.mobile)+"sell", value=jobject, time=60*15)
                    estate_buy =  [ _estate_ for _estate_ in list(queryset) if _estate_["estate_status"] == "buy" ]
                    jobject = json.dumps(estate_buy)
                    if len(estate_buy):
                        cache.setex(name= str(request.user.mobile)+"buy", value=jobject, time=60*15)
                except:
                    pass
                return ReturnResponse(success=True,msg="Created Successfully", status=status.HTTP_201_CREATED)
            else:

                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            mycol = db.property_estatestatus
            queryset = mycol.find({"is_deleted":False})
            if "estate_status" in cache:
                estate_status = cache.get("estate_status")
                estate_status = json.loads(estate_status)
                data = estate_status
            else:
                serializer = EstateStatusSerializer(queryset,many = True)
                jobject = json.dumps(serializer.data)
                cache.setex(name= "estate_status", value=jobject, time=60*60)
                data = serializer.data
            return ReturnResponse(data = data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateEstateStatusAPIView(CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer

    def post(self,request):
        try:
            serializer = EstateStatusSerializer(data=request.data)

            if serializer.is_valid():
                estate_status,created = EstateStatus.objects.get_or_create(
                    estate_status_name = serializer.data["estate_status_name"]
                )
                estate_status.save()


                return ReturnResponse(success=True,msg="Created Successfully", status=status.HTTP_200_OK)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateEstateStatusAPIView(UpdateAPIView):
    queryset = EstateStatus.objects.all()
    serializer_class = EstateStatusSerializer
    def put(self,request,**kwargs):
        try:
            serializer = EstateStatusSerializer(data=request.data)
            id = kwargs.get('pk',0)
            if serializer.is_valid():
                try:
                    estate_status = EstateStatus.objects.get(pk = id)
                    estate_status.estate_status_name = serializer.data["estate_status_name"]
                    estate_status.save()

                    return ReturnResponse(success=True,msg="Updated Successfully", status=status.HTTP_200_OK)
                except Exception as e:
                    return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

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
        try:
            if "estate_type" in cache:
                estate_types = cache.get("estate_type")
                estate_types = json.loads(estate_types)
                data = estate_types
            else:
                mycol = db.property_estatetype
                queryset = mycol.find({"is_deleted":False})
                serializer = EstateTypeSerializer(queryset,many = True)
                jobject = json.dumps(serializer.data)
                cache.setex(name= "estate_type", value=jobject, time=60*60)
                data = serializer.data
            return ReturnResponse(data = data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        



class CreateEstateTypeAPIView(CreateAPIView):
    queryset = EstateType.objects.all()
    serializer_class = EstateTypeSerializer

    def post(self,request):
        try:
            serializer = EstateTypeSerializer(data=request.data)

            if serializer.is_valid():
                estate_type,created = EstateType.objects.get_or_create(
                    type_name = serializer.data["type_name"]
                )
                estate_type.save()

                return ReturnResponse(success=True,msg="Created Successfully", status=status.HTTP_200_OK)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEstateTypeAPIView(UpdateAPIView):
    queryset = EstateType.objects.all()
    serializer_class = EstateTypeSerializer
    def put(self,request,**kwargs):
        try:
            serializer = EstateTypeSerializer(data=request.data)
            id = kwargs.get('pk',0)
            if serializer.is_valid():
                try:
                    estate_type = EstateType.objects.get(pk = id)
                    estate_type.type_name = serializer.data["type_name"]
                    estate_type.save()

                    return ReturnResponse(success=True,msg="Updated Successfully", status=status.HTTP_200_OK)
                except Exception as e:
                        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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



@api_view(('POST',))
@parser_classes([JSONParser,])
@csrf_exempt
def related_properties(request):
    try:
        queryset = []
        if not "estate" in request.data.keys() and request.data["estate"]:
            context = {
                "msg": "Please Provide estates"
            }
            return Response(data=context, status=status.HTTP_400_BAD_REQUEST)

        else:
            findQuery = request.data["estate"]
            mycol = db.property_estate
            queryset = find_related_db(mycol,findQuery)

        if queryset:
            serializer = EstateSerializer(queryset,many = True)
            return ReturnResponse(data=serializer.data,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        else:
            return ReturnResponse(success=True,msg="no data found", status=status.HTTP_200_OK)
    except Exception as e:
        return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
