from django.urls import path
from django.conf.urls import  url
from chat import  views

urlpatterns = [
    path("create/", views.CreateMessageAPIView.as_view(),name="Messages_create"),
    path("contactlist/", views.ListContactAPIView.as_view(), name="contact_list"),
    path("chatbymobile/",views.chatByMobile , name="chat_by_mobile"),
    path("reply/", views.demo_reply, name="chat_reply"),
    url(r'^$', views.index, name='index'),
    url(r'^(?P<chat_room_id>\d+)/$', views.chat_room, name='chat_room'),
    url(r'^long_poll/(?P<chat_room_id>\d+)/$', views.longpoll_chat_room, name='longpoll_chat_room'),
]