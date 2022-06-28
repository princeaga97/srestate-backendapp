from dataclasses import fields
from rest_framework import serializers
from chat.models import Contacts, Messages






class MessageSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = Messages
        exclude = ["sent","sender_name","time","timestamp"]

class MessageViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        fields = "__all__"
    
    def get_timestamp(self, obj):
        return obj.timestamp.total_seconds()


class ContactViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    last_message = MessageSerializer()
    
    class Meta:
        model = Contacts
        fields = "__all__"
    def get_timestamp(self, obj):
        return obj.timestamp.total_seconds()