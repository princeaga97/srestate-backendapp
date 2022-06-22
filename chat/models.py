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
        return f"To: {self.receiver_name} From: {self.sender_name}"

    class Meta:
        ordering = ('timestamp',)
        app_label = 'chat'


class Contacts(models.Model):

    last_message =  models.ForeignKey(Messages, on_delete=models.CASCADE, related_name='latest_msg',null=True,blank=True)
    contact = models.TextField(blank=False)
    owner = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To: {self.contact} From: {self.last_message.description}"

    class Meta:
        ordering = ('timestamp',)
        app_label = 'chat'