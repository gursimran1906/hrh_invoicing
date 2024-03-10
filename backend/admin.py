from django.contrib import admin
from .models import Room, LocalAuthority, Client, Invoice, Rate, MoneyIn, OneToOne, OneToOneAgency, Attendance, CreditNote
from simple_history.admin import SimpleHistoryAdmin


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_shared')

@admin.register(Attendance)
class AttendaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date', 'present')


@admin.register(LocalAuthority)
class LocalAuthorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'email', 'contact_number', 'timestamp')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'contact_number', 'date_joined', 'date_left', 'email',
                    'client_types', 'client_agreed_rate',  'allotted_room', 'payable_by',
                    'resident_name_number', 'timestamp')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ( 'invoice_number', 'client', 'costs', 'settled', 'timestamp')

@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'invoice_to_allocate','notes', 'timestamp')


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'amount', 'timestamp')

@admin.register(MoneyIn)
class MoneyInAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_type', 'amount', 'date', 'timestamp')


@admin.register(OneToOne)
class OneToOneAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'hours', 'customer')

@admin.register(OneToOneAgency)
class OneToOneAgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'rate')
