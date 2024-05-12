from django.db import models

# Create your models here.
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    address = models.TextField()
    no_of_available_invoice_users = models.IntegerField() 
    no_of_available_admin_users = models.IntegerField()
    paid_until =  models.DateField()
    on_trial = models.BooleanField()
    bank_name=models.CharField(max_length=100)
    bank_account_name = models.CharField(max_length=100)
    bank_account_no=models.IntegerField() 
    bank_sort_code=models.CharField(max_length=100)
    invoice_footer = models.TextField()
    one_to_one_rate_hourly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

class Domain(DomainMixin):
    pass