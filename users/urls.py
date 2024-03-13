from django.contrib import admin
from django.urls import path
from .views import login_view, logout_view, register_user, all_users, send_password_reset, CustomPasswordResetConfirmView, remove_or_restrict_user, activate_user

urlpatterns = [
    
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_user, name='register_new_user'),
    path('deactivate/<int:user_id>/',remove_or_restrict_user,name='deactivate_user'),
    path('activate/<int:user_id>/',activate_user,name='activate_user'),
    path('send_password_reset/<int:user_id>/',send_password_reset,name='send_password_reset_email'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='custom_password_reset_confirm'),
    path('all/', all_users, name='all_users'),
]