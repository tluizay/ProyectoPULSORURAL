from django.urls import path
from . import views


urlpatterns = [
    path("rendimientos/", views.api_ine, name="rendimientos"),
    
]