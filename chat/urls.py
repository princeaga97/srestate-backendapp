from django.urls import path
from django.conf.urls import  url
from chat import  views

urlpatterns = [
    path("create/", views.CreateMessageAPIView.as_view(),name="Messages_create"),
    path("contactlist/", views.ListContactAPIView.as_view(), name="contact_list"),
    path("chatbymobile/",views.chatByMobile , name="chat_by_mobile"),
    path("reply/", views.demo_reply, name="chat_reply"),
]