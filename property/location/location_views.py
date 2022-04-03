from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status

from property.location.location_serializers import CitySerializer, AreaSerializer, ApartmentSerializer
from property.models import Area,City, Apartment


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
    queryset = Area.objects.filter(is_deleted = 0)
    serializer_class = AreaSerializer

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
    serializer_class = ApartmentSerializer

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





