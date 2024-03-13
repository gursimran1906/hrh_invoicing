from django.db import models

# Create your models here.
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    no_of_available_invoice_users = models.IntegerField() 
    no_of_available_admin_users = models.IntegerField()
    paid_until =  models.DateField()
    on_trial = models.BooleanField()
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

class Domain(DomainMixin):
    pass