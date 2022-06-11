from dataclasses import fields
from email.policy import default
from typing_extensions import Required
from rest_framework import serializers
from property.models import Estate, EstateStatus, EstateType,photos,City,Apartment


class EstateSerializer(serializers.ModelSerializer):
    def create(self,validate_data):
        return Estate.objects.create(**validate_data)

    class Meta:
        model = Estate
        fields = ["id","estate_name","city","estate_type","floor_space",
        "number_of_bedrooms","estate_description","estate_status","society",
        "area","budget","furniture" ]





class EstateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateStatus
        exclude = ["is_deleted"]


class EstateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateType
        fields = ["type_name" ]


class ImageSerializer(serializers.ModelSerializer):

    def create(self,validate_data):
        return photos.objects.create(**validate_data)

    class Meta:
        model = photos
        fields = '__all__'


class EstateWPSerializer(serializers.Serializer):
    string = serializers.CharField()
    #mobile  = serializers.CharField(max_length = 10)