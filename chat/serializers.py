from dataclasses import fields
from rest_framework import serializers
from chat.models import Contacts, Messages 
from rest_framework.fields import CurrentUserDefault






class MessageSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = Messages
        exclude = ["sent","sender_name","time","timestamp"]

class MessageViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    sent = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        exclude = ["time"]
    
    def get_timestamp(self, obj):
        return int(obj.timestamp.timestamp())
    
    def get_sent(self,obj):
        if obj.sender_name == self.context["request"].user.username:
            return True
        return False
    




class ContactViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    last_message = MessageSerializer()
    
    class Meta:
        model = Contacts
        fields = "__all__"
    def get_timestamp(self, obj):
        return int(obj.last_message.timestamp.timestamp())
    
    def get_websocket_url(self,obj):
        return f"wss://srestatechat.herokuapp.com/ws/chat/{obj.owner}_{obj.contact}/"