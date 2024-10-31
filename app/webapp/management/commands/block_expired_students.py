from django.core.management.base import BaseCommand
from django.utils import timezone
from webapp.models import studRec

class Command(BaseCommand):
    help = 'Set students to inactive if their expiration date has passed'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired_students = studRec.objects.filter(expiration__lt=today, status='Active')
        expired_count = expired_students.update(status='Inactive')
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {expired_count} students to Inactive'))
    