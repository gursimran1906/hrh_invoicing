from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField()
    is_invoice_department = models.BooleanField(null=True)
    tenant = models.CharField(max_length=20, default='public')
    def __str__(self):
        return self.username
    