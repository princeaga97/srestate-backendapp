from dataclasses import fields
from rest_framework import serializers
from chat.models import Contacts, Messages






class MessageSerializer(serializers.ModelSerializer):
    def create(self,validate_data):
        return Messages.objects.create(**validate_data)

    class Meta:
        model = Messages
        exclude = ["sent","sender_name","time","timestamp"]

class MessageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"


class ContactViewSerializer(serializers.ModelSerializer):
    last_message = MessageSerializer()
    class Meta:
        model = Contacts
        fields = "__all__"