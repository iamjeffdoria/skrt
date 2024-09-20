from django.db import models
from PIL import Image
# Create your models here.
import io
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password,check_password




class HeadOfSecurity(models.Model):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    
    picture = models.ImageField(upload_to='security_pictures/', null=True, blank=True)
    password = models.CharField(max_length=128)  # Hashed password

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Hash password only when the instance is created
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        
        # Resize and crop the picture
        if self.picture:
            with Image.open(self.picture.path) as img:
                min_dimension = min(img.size)
                left = (img.width - min_dimension) // 2
                top = (img.height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
                img.save(self.picture.path)


class UserProfile(models.Model):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('head_of_security', 'Head of Security'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user_type == 'admin':
            self.user.is_superuser = True
            self.user.is_staff = True
            self.user.save()
        if self.picture:
            with Image.open(self.picture.path) as img:
                min_dimension = min(img.size)
                left = (img.width - min_dimension) // 2
                top = (img.height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
                img.save(self.picture.path)
# New model for Departments

COURSE_CHOICES = [
    ('BSMT', 'Bachelor of Science in Marine Transportation'),
    ('BSMar-E', 'Bachelor of Science in Marine Engineering'),   
    ('BEEd', 'Bachelor of Elementary Education'),
    ('BSed', 'Bachelor of Secondary Education'),
    ('BTLEd', 'Bachelor of Technology and Livelihood Education'),
    ('BTVTEd', 'Bachelor of Technical Vocational Teacher Education'),
    ('BPEd', 'Bachelor of Physical Education'),
    ('BACom', 'Bachelor of Arts in Communication'),
    ('BSHM', 'Bachelor of Science in Hospitality Management'),
    ('BSBA', 'Bachelor of Science in Business Administration major in Marketing Management'),
    ('BSMarBio', 'Bachelor of Science in Marine Biology'),
    ('BSIE', 'Bachelor of Science in Industrial Engineering'),
    ('BSME', 'Bachelor of Science in Mechanical Engineering'),
    ('BSEE', 'Bachelor of Science in Electrical Engineering'),
    ('BSIT', 'Bachelor of Science in Information Technology'),
    ('BSInT', 'Bachelor of Science in Industrial Technology'),
]

MAJOR_CHOICES = [
    ('English', 'English'),
    ('Filipino', 'Filipino'),
    ('Mathematics', 'Mathematics'),
    ('Social Studies', 'Social Studies'),
    ('Automative', 'Automative'),
    ('Drafting', 'Drafting'),
    ('Electrical', 'Electrical'),
    ('Electronics', 'Electronics'),
    ('Fashion and Apparel', 'Fashion and Apparel'),
    ('Food and Beverages Preparation Service Management', 'Food and Beverages Preparation Service Management'),
    ('Mechanical', 'Mechanical'),
    ('Powerplant', 'Powerplant'),
    ('Welding and Fabrication', 'Welding and Fabrication'),
    ('No Major', 'No Major'),
]

class studRec(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    student_id = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    rfid_number = models.CharField(max_length=50)
    course = models.CharField(max_length=200, choices=COURSE_CHOICES, null=True, blank=True)  # Static choices
    major = models.CharField(max_length=200, choices=MAJOR_CHOICES, null=True, blank=True)  # Static choices
    picture = models.ImageField(upload_to='student_pictures/', null=True, blank=True)
    status = models.CharField(max_length=10, default='Active')

    # New fields
    email = models.EmailField(validators=[EmailValidator()], unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name} {self.suffix if self.suffix else ''}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            with Image.open(self.picture.path) as img:
                # Ensure the image is square
                min_dimension = min(img.size)
                left = (img.width - min_dimension) // 2
                top = (img.height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
                img.save(self.picture.path)


class PendingRequests(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    student_id = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    course = models.CharField(max_length=200, choices=COURSE_CHOICES, null=True, blank=True)
    major = models.CharField(max_length=200, choices=MAJOR_CHOICES, null=True, blank=True)
    picture = models.ImageField(upload_to='student_pictures/', null=True, blank=True)
    status = models.CharField(max_length=10, default='Pending')

    # New fields
    email = models.EmailField(validators=[EmailValidator()], unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name} {self.suffix if self.suffix else ''}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            with Image.open(self.picture.path) as img:
                min_dimension = min(img.size)
                left = (img.width - min_dimension) // 2
                top = (img.height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
                img.save(self.picture.path)


class AttendanceLog(models.Model):
    student = models.ForeignKey(studRec, on_delete=models.CASCADE)  # Link to studRec
    student_reference_id = models.CharField(max_length=20)  # Unique identifier based on student_id from studRec
    type = models.CharField(max_length=10, choices=[('login', 'Login'), ('logout', 'Logout')])  # Type of entry
    time = models.DateTimeField(default=timezone.now)  # Timestamp for the record
    date_in = models.DateField(blank=True, null=True)  # Date of login
    date_out = models.DateField(blank=True, null=True)  # Date of logout
    note = models.CharField(max_length=255, blank=True, null=True)  # Additional notes

    def __str__(self):
        return f"{self.student} - {self.type} at {self.time}"
    
class Report(models.Model):
    student_id = models.CharField(max_length=20)
    rfid_loss_date = models.DateField()
    report_content = models.TextField()
    date_submitted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report by {self.student_id} on {self.rfid_loss_date}"
    
    