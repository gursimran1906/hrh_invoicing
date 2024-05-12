from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_invoice_department = models.BooleanField(null=True, default=True)
    tenant = models.CharField(max_length=20, default='public')
    
    def __str__(self):
        return self.username
    