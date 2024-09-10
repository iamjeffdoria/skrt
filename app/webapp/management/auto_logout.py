# webapp/management/commands/auto_logout.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from webapp.models import AttendanceLog,studRec
from datetime import timedelta

class Command(BaseCommand):
    help = 'Automatically log out students who did not log out by midnight'

    def handle(self, *args, **kwargs):
        # Get the current time and the start of the current day
        now = timezone.now()
        start_of_today = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)

        # Find all login logs from the previous day where there is no corresponding logout log
        login_logs = AttendanceLog.objects.filter(type='login', time__lt=start_of_today)

        for log in login_logs:
            # Check if there is a corresponding logout log after the login
            corresponding_logout = AttendanceLog.objects.filter(student=log.student, type='logout', time__gt=log.time).first()
            
            if not corresponding_logout:
                # If no corresponding logout log exists, create a logout log at midnight
                logout_time = log.time + timedelta(hours=23, minutes=59, seconds=59)
                AttendanceLog.objects.create(
                    student=log.student,
                    student_reference_id=log.student_reference_id,
                    type='logout',
                    time=logout_time,
                    date_out=logout_time.date(),
                    note='Auto logout by system'
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully logged out {log.student} who did not logout by midnight'))
