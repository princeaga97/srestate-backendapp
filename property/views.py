from rest_framework.generics import ListAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView

from property.estate.estate_serializers import EstateSerializer
from property.models import Estate


# Create your views here.
class ListEstateAPIView(ListAPIView):
    """This endpoint list all of the available todos from the database"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class CreateEstateAPIView(CreateAPIView):
    """This endpoint allows for creation of a todo"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class UpdateEstateAPIView(UpdateAPIView):
    """This endpoint allows for updating a specific todo by passing in the id of the todo to update"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class DeleteEstateAPIView(DestroyAPIView):
    """This endpoint allows for deletion of a specific Estate from the database"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer


