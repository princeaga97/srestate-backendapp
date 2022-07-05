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
        return obj.timestamp.timestamp()




class ContactViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    last_message = MessageSerializer()
    webseocket_url = serializers.CharField()
    
    class Meta:
        model = Contacts
        fields = "__all__"
    def get_timestamp(self, obj):
        return obj.timestamp.timestamp()
    
    def get_webseocket_url(self,obj):
        return f"wss://srestatechat.herokuapp.com/ws/chat/{obj.owner}_{obj.contact}/"