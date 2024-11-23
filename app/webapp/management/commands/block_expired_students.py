from django.core.management.base import BaseCommand
from django.utils import timezone
from webapp.models import studRec
import os
class Command(BaseCommand):
    help = 'Set students to inactive if their expiration date has passed'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired_students = studRec.objects.filter(expiration__lt=today, status='Active')
        expired_count = expired_students.update(status='Inactive')
        
        # Create or append to a log file
        log_directory = 'logs'
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, 'student_inactivation_log.txt')
        
        with open(log_file_path, 'a') as log_file:
            log_message = f"{timezone.now()}: Successfully updated {expired_count} students to Inactive\n"
            log_file.write(log_message)
        
        self.stdout.write(self.style.SUCCESS(log_message))
    