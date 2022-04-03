from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from property.estate.estate_serializers import EstateSerializer, EstateStatusSerializer, EstateTypeSerializer,ImageSerializer
from property.models import Estate, EstateStatus, EstateType ,photos,City,Apartment,Area , Broker


def modify_input_for_multiple_files(estate_id, image):
    dict = {}
    dict['estate_id'] = estate_id
    dict['image'] = image
    return dict



# Create your views here.
class ListEstateAPIView(ListAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class CreateEstateAPIView(CreateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

    def post(self,request,mobile):
        serilizer = EstateSerializer(data=request.data)
        if len(str(mobile)) == 10:
            broker,created = broker.objects.get_or_create(
            name = serilizer.data["broker_name"],
            mobile = int(mobile)
            )
        print(request.data)
        if serilizer.is_valid():
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





