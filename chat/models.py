from operator import mod
from django.db import models

# Create your models here.



class Messages(models.Model):

    description = models.TextField(blank=False)
    sender_name = models.TextField(blank=False)
    receiver_name = models.TextField(blank=False)
    time = models.TimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.timestamp = self.timestamp.total_seconds()
        self.save()
        return f"To: {self.receiver_name} From: {self.sender_name}"

    class Meta:
        ordering = ('timestamp',)
        app_label = 'chat'


class Contacts(models.Model):

    last_message =  models.ForeignKey(Messages, on_delete=models.CASCADE, related_name='latest_msg',null=True,blank=True)
    contact = models.TextField(blank=False)
    owner = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    websocket_url = models.TextField(blank=True,default="")

    def __str__(self):
        self.websocket_url = f"wss://srestatechat.herokuapp.com/ws/chat/{self.owner}_{self.contact}/"
        self.save()
        return f"To: {self.contact} From: {self.last_message.description}"

    class Meta:
        ordering = ('timestamp',)
        app_label = 'chat'

