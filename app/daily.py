import schedule
import time
import django
import os
from datetime import datetime
import logging

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from django.utils import timezone
from webapp.models import studRec

# Configure logging to a file
logging.basicConfig(filename="block_students.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def block_expired_students():
    # Get the current date
    now = timezone.now().date()
    
    # Query for students with expiration dates today or in the past who are still active
    expired_students = studRec.objects.filter(expiration__lte=now, status='Active')
    
    # Count the students before updating
    expired_count = expired_students.count()
    
    # Update the status of expired students to 'Inactive'
    expired_students.update(status='Inactive')
    
    # Print and log a summary of the action taken
    message = f"{expired_count} students have been blocked"
    print(f'{datetime.now()} - {message}')
    logging.info(message)

# Schedule the task to run daily at a specific time
schedule.every().day.at("09:37").do(block_expired_students)

while True:
    schedule.run_pending()
    time.sleep(60)
