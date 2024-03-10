# your_app_name/cron.py

from django.core.mail import EmailMessage
from django.utils import timezone
from django_cron import CronJobBase, Schedule
from .models import Attendance
from datetime import datetime



class DailyCheckForUnmarkedAttendance(CronJobBase):
    RUN_EVERY_MINS = 1  # every 15 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'backend.daily_check_for_unmarked_attendance'

    def do(self):
        # Get the date one day ago
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        
        unmarked_attendance = Attendance.objects.filter(date__lte=one_day_ago,)
        print('Cron Test')
        today_date = datetime.now().strftime('%d-%m-%Y')
        if not unmarked_attendance.exists():
            # Send email to someone
            subject = f'Unmarked Attendance Reminder for {one_day_ago} ({today_date})'
            message = 'Dear Admin Staff,\n\nSome Attendance entries are not marked. Please check and mark them.\n\nKind regards\nCareOps'
            recipient_email = 'gursimran1906@gmail.com'

            email = EmailMessage(subject, message, to=[recipient_email])

            email.send()
