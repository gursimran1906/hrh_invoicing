from django.db import models
from datetime import date
from simple_history.models import HistoricalRecords





class Room(models.Model):
    id = models.AutoField(primary_key=True)
    is_shared = models.BooleanField(default=False)
    history = HistoricalRecords()
    def __str__(self):
        return str(self.id)

class LocalAuthority(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    hide_client_deatils = models.BooleanField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return f'{self.name} - {self.address}'

class Rate(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return f'{self.description} - £{self.amount}'

class Client(models.Model):
    CLIENT_TYPE_CHOICES = {
        ('private_funded', 'Private Funded'),
        ('authorities_funded', 'Authorities Funded'),
    }
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    date_joined = models.DateField()
    date_left = models.DateField(null=True, blank=True)
    email = models.EmailField()
    client_types = models.CharField(max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='private_funded') 
    client_agreed_rate = models.ForeignKey(Rate, on_delete=models.CASCADE, null=True)
    allotted_room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    payable_by = models.ForeignKey(LocalAuthority, on_delete=models.CASCADE, null=True, blank=True)
    resident_name_number = models.CharField(max_length=255)
    respite = models.BooleanField(null=True)
    notes = models.TextField(null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return f'{self.name} - {self.address}'

class OneToOneAgency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

class OneToOne(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    hours = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    history = HistoricalRecords()

   
    
    def __str__(self):
        return str(self.customer) +', hours: '+str(self.hours)
    
class MoneyIn(models.Model):
    id = models.AutoField(primary_key=True)
    payment_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_left = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    desc = models.CharField(max_length=255, default='')
    date = models.DateField()
    invoices_to_allocate = models.ManyToManyField('Invoice', related_name='monies_in', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def save(self, *args, **kwargs):
        if self.balance_left is None:
            self.balance_left = self.amount
        super(MoneyIn, self).save(*args, **kwargs)

class Invoice(models.Model):
    invoice_number = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=date.today)
    desc = models.ForeignKey(Rate,on_delete=models.CASCADE, null=True)
    costs = models.DecimalField(max_digits=10, decimal_places=2)
    units = models.IntegerField(default=1)
    settled = models.BooleanField(default=False)
    sent_to_client = models.BooleanField(default=False)
    additional_notes = models.CharField(max_length=255, blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return str(self.invoice_number)


class CreditNote(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_to_allocate = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    notes = models.CharField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def is_invoice_settled(self):
        return self.invoice_to_allocate.settled  

    def save(self, *args, **kwargs):
        if not self.is_invoice_settled():
            print(self.invoice_to_allocate.settled)
            self.invoice_to_allocate.settled = True
            print(self.invoice_to_allocate.settled)
            self.invoice_to_allocate.save()
            super().save(*args, **kwargs)
        else:
            raise Exception("Cannot save CreditNote for an already settled invoice.")
    
    def __str__(self) -> str:
        return f'Credit Note {str(self.id)} for Invoice: {self.invoice_to_allocate}'

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    present = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    def __str__(self):
        return f'{self.client.name} - {self.date} - Present: {self.present}'
         
