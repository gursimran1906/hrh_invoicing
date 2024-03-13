from django.contrib import admin
from django.urls import path
from .views import all_org_clients

urlpatterns = [
    
    path('care_homes/', all_org_clients, name='all_org_clients'),
]