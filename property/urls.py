from django.urls import path,include

from property.estate import estate_views as views

urlpatterns = [
    path("",include("property.estate.urls")),
    path("",include("property.location.urls"))

]