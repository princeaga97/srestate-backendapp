from urllib.parse import quote_from_bytes
from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
import pymongo
from srestate.settings import mongo_uri,CACHES
import json
import redis

from property.location.location_serializers import ApartmentbulkSerializer, BrokerSerializer, CitySerializer, AreaSerializer, ApartmentSerializer ,ApartmentlistSerializer
from property.models import Area, Broker,City, Apartment


cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])

print(mongo_uri)
client = pymongo.MongoClient(mongo_uri)
db = client['your-db-name']

# Create your views here.
class ListCityAPIView(ListAPIView):
    queryset = City.objects.filter(is_deleted = 0)
    serializer_class = CitySerializer

class CreateCityAPIView(CreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class UpdateCityAPIView(UpdateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class DeleteCityAPIView(DestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class ListAreaAPIView(ListAPIView):
    serializer_class = AreaSerializer
    def get(self,request):
        mycol = db.property_area
        queryset = mycol.find({"is_deleted":False})
        if "area" in cache:
            areas = cache.get("area")
            if queryset.count()!= len(areas):
                serializer = AreaSerializer(queryset,many = True)
                print(serializer)
                jobject = json.dumps(serializer.data)
                cache.setex(name = request.user.mobile, value=jobject, time=60*60*24)
                return Response(data=jobject, status=status.HTTP_200_OK)
            else:
                return Response(areas, status=status.HTTP_200_OK)
        serializer = AreaSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= "area", value=jobject, time=60*60*24)
        return Response(data=jobject, status=status.HTTP_200_OK)

class CreateAreaAPIView(CreateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

    def post(self,request):
        serilizer = AreaSerializer(data=request.data)

        if serilizer.is_valid():

            area,created = Area.objects.get_or_create(
                area_name = serilizer.data["area_name"],
                city = City.objects.get(pk=serilizer.data["city"]),
                pincode = serilizer.data["pincode"]
            )
            area.save()

            context = {
                "msg":"Created Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)



class UpdateAreaAPIView(UpdateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    def put(self,request,**kwargs):
        serilizer = AreaSerializer(data=request.data)
        id = kwargs.get('pk',0)
        if serilizer.is_valid():
            try:
                area = Area.objects.get(pk = id)
                area.area_name = serilizer.data["area_name"]
                area.city = City.objects.get(pk=serilizer.data["city"])
                area.pincode = serilizer.data["pincode"]
                area.save()

                context = {
                    "msg":"Updated Successfully"
                }

                return Response(context, status=status.HTTP_200_OK)

            except Area.DoesNotExist:
                context = {
                    "msg": "Record Does Not Exists"
                }

                return Response(context, status=status.HTTP_200_OK)


        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class DeleteAreaAPIView(DestroyAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk',0)
        try:
            area = Area.objects.get(pk = id)
            area.is_deleted = True
            area.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except Area.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)







class ListApartmentAPIView(ListAPIView):
    queryset = Apartment.objects.filter(is_deleted = 0)
    serializer_class = ApartmentlistSerializer
    def get(self,request):
        client = pymongo.MongoClient(mongo_uri)
        db = client['your-db-name']
        mycol = db.property_apartment
        if "area" in request.data:
            queryset = mycol.find({"is_deleted":False,"area":request.data["area"]})
        else:
            queryset = mycol.find({"is_deleted":False})
        serializer = ApartmentSerializer(queryset,many = True)
        jobject = json.dumps(serializer.data)
        cache.setex(name= "area", value=jobject, time=60*60*24)
        return Response(data=jobject, status=status.HTTP_200_OK)

class CreateBulkApartmentAPIView(CreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentbulkSerializer

    def post(self,request):
        context = []
        print("hello")
        apartmentlist = request.data["apartmentlist"]
        for data in apartmentlist:
            print(data)
            apartment,created = Apartment.objects.get_or_create(
                apartment_name = data["apartment_name"].lower(),
                area = data["area"].lower()
            )
            apartment.save()

            context.append({
                "msg":"Created Successfully"
            })
        

            
        
        return Response(context, status=status.HTTP_200_OK)


class CreateBrokerAPIView(CreateAPIView):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer

    def post(self,request):
        serilizer = BrokerSerializer(data=request.data)

        if serilizer.is_valid():
            try:
                mycol = db.property_broker
                updatestmt = (
                    {"mobile":"8128975337"},
                    {"$set":{
                        "name": serilizer.data["name"],
                        "area": serilizer.data["area"],
                        "estate_type": serilizer.data["estate_type"],
                        "balance":1000
                    }}
                )
                broker = mycol.update_one(*updatestmt)

                if broker.raw_result["n"] == 0:
                    print(broker.raw_result)

                context = {
                    "msg":"Broker Created Successfully"
                }

                return Response(context, status=status.HTTP_200_OK)
            except Exception as e:
                return Response("Exception "+str(e), status=status.HTTP_400_BAD_REQUEST)

        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)




class CreateApartmentAPIView(CreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

    def post(self,request):
        serilizer = ApartmentSerializer(data=request.data)

        if serilizer.is_valid():
            apartment,created = Apartment.objects.get_or_create(
                apartment_name = serilizer.data["apartment_name"],
                area = Area.objects.get(pk=serilizer.data["area"]),
            )
            apartment.save()

            context = {
                "msg":"Created Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UpdateApartmentAPIView(UpdateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    def put(self,request,**kwargs):
        serilizer = ApartmentSerializer(data=request.data)
        id = kwargs.get('pk',0)
        if serilizer.is_valid():
            try:
                apartment = Apartment.objects.get(pk = id)
                apartment.apartment_name = serilizer.data["apartment_name"]
                apartment.area = Area.objects.get(pk=serilizer.data["area"])
                apartment.save()

                context = {
                    "msg":"Updated Successfully"
                }

                return Response(context, status=status.HTTP_200_OK)

            except Apartment.DoesNotExist:
                context = {
                    "msg": "Record Does Not Exists"
                }

                return Response(context, status=status.HTTP_200_OK)

        else:
            context = {
                "msg": serilizer.errors
            }

            return Response(context, status=status.HTTP_201_CREATED)

class DeleteApartmentAPIView(DestroyAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk','0')
        try:
            apartment = Apartment.objects.get(pk = id)
            apartment.is_deleted = 1
            apartment.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except Apartment.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)





