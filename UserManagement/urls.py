from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from UserManagement.views import   validate_mobile

urlpatterns = [
    path("validate_mobile", validate_mobile , name ='validate_mobile' )
    ]

urlpatterns += staticfiles_urlpatterns()