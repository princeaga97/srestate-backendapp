from dataclasses import fields
from rest_framework import serializers
from property.models import City,Area,Apartment, Broker


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        exclude = ["is_deleted"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ["is_deleted"]


class BrokerSerializer(serializers.ModelSerializer):
    area = serializers.ListField(
            child=serializers.CharField(max_length = 1000)
            )
    estate_type = serializers.ListField(
            child=serializers.CharField(max_length = 1000)
            )
    class Meta:
        model = Broker
        exclude = ["mobile"]

class BrokerBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ["mobile","balance"]


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        exclude = ["is_deleted"]


class ApartmentlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ["area"]

class ApartmentbulkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ["apartment_name","area"]