from django.core.mail import EmailMessage
from django.utils import timezone
from django_cron import CronJobBase, Schedule
from django_tenants.utils import schema_context
from .models import Attendance
from datetime import datetime
from organisation.models import Client
from users.models import CustomUser


def daily_check_for_unmarked_attendance():
    try:
        for tenant in Client.objects.all():  
            with schema_context(tenant.schema_name):
                users = CustomUser.objects.filter(tenant=tenant.name)
                recipient_emails = [user.email for user in users]
                invoice_users = CustomUser.objects.filter(is_invoice_department=True)
                recipient_emails.extend(user.email for user in invoice_users)
                check_unmarked_attendance(recipient_emails,tenant.name)

    except Exception as e:
        print(e)

def check_unmarked_attendance(recipient_emails, tenant_name):
    print(f'running checks for attendances at {tenant_name}')
    one_day_ago = timezone.now() - timezone.timedelta(days=1)
    unmarked_attendance = Attendance.objects.filter(date=one_day_ago)
    one_day_ago = one_day_ago.strftime('%d-%m-%Y')
    if not unmarked_attendance.exists():
        subject = f'Unmarked Attendance Reminder for {tenant_name.capitalize()} of {one_day_ago}'
        message = f'Dear Admin Staff,\n\nAttendance not marked. Please mark attendace for {one_day_ago}.\n\nKind regards\nCareOps'
        email = EmailMessage(subject, message, to=recipient_emails)
        emails = email.send()
        print('emails sent', emails)
    else: 
        print('Checking regular attendance - attendance marked')
