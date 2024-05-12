from django.contrib import admin
from django.urls import path
from .views import all_org_clients, amend_client_details

urlpatterns = [
    path('care_home/edit/<int:id>/', amend_client_details, name='amend_care_home'),
    path('care_homes/', all_org_clients, name='all_org_clients'),
]