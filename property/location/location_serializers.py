from rest_framework import serializers
from property.models import City,Area,Apartment


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        exclude = ["is_deleted"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ["is_deleted"]


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        exclude = ["is_deleted"]
