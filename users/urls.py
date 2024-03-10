from django.contrib import admin
from django.urls import path
from .views import login_view, logout_view, register_user

urlpatterns = [
    
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
     path('register/', register_user, name='register_new_user'),
]