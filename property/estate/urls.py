from django.urls import path, re_path

from property.estate import estate_views as views

urlpatterns = [
    path("estate/",views.ListEstateAPIView.as_view(),name="estate_list"),
    re_path(r'^estate/(?P<mobile>\d{0,50})/create/', views.CreateEstateAPIView.as_view(),name="estate_create"),
    path("estate/update/<int:pk>/",views.UpdateEstateAPIView.as_view(),name="update_estate"),
    path("estate/delete/<int:pk>/",views.DeleteEstateAPIView.as_view(),name="delete_estate"),
    path("estate_status/",views.ListEstateStatusAPIView.as_view(),name="estate_status_list"),
    path("estate_status/create/", views.CreateEstateStatusAPIView.as_view(),name="estate_status_create"),
    path("estate_status/update/<int:pk>/",views.UpdateEstateStatusAPIView.as_view(),name="update_estate_status"),
    path("estate_status/delete/<int:pk>/",views.DeleteEstateStatusAPIView.as_view(),name="delete_estate_status"),
	path("estate_type/",views.ListEstateTypeAPIView.as_view(),		  		  name="estate_type_list"),
    path("estate_type/create/", views.CreateEstateTypeAPIView.as_view(),		  name="estate_type_create"),
    path("estate_type/update/<int:pk>/",views.UpdateEstateTypeAPIView.as_view(),name="update_estate_type"),
    path("estate_type/delete/<int:pk>/",views.DeleteEstateTypeAPIView.as_view(),name="delete_estate_type")
]