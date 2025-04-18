# Generated by Django 5.0.4 on 2024-08-29 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0032_delete_studreg'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('student_id', models.CharField(max_length=20)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('suffix', models.CharField(blank=True, max_length=10, null=True)),
                ('course', models.CharField(blank=True, choices=[('BSMT', 'Bachelor of Science in Marine Transportation'), ('BSMar-E', 'Bachelor of Science in Marine Engineering'), ('BEEd', 'Bachelor of Elementary Education'), ('BSed', 'Bachelor of Secondary Education'), ('BTLEd', 'Bachelor of Technology and Livelihood Education'), ('BTVTEd', 'Bachelor of Technical Vocational Teacher Education'), ('BPEd', 'Bachelor of Physical Education'), ('BACom', 'Bachelor of Arts in Communication'), ('BSHM', 'Bachelor of Science in Hospitality Management'), ('BSBA', 'Bachelor of Science in Business Administration major in Marketing Management'), ('BSMarBio', 'Bachelor of Science in Marine Biology'), ('BSIE', 'Bachelor of Science in Industrial Engineering'), ('BSME', 'Bachelor of Science in Mechanical Engineering'), ('BSEE', 'Bachelor of Science in Electrical Engineering'), ('BSIT', 'Bachelor of Science in Information Technology'), ('BSInT', 'Bachelor of Science in Industrial Technology')], max_length=200, null=True)),
                ('major', models.CharField(blank=True, choices=[('English', 'English'), ('Filipino', 'Filipino'), ('Mathematics', 'Mathematics'), ('Social Studies', 'Social Studies'), ('Automative', 'Automative'), ('Drafting', 'Drafting'), ('Electrical', 'Electrical'), ('Electronics', 'Electronics'), ('Fashion and Apparel', 'Fashion and Apparel'), ('Food and Beverages Preparation Service Management', 'Food and Beverages Preparation Service Management'), ('Mechanical', 'Mechanical'), ('Powerplant', 'Powerplant'), ('Welding and Fabrication', 'Welding and Fabrication'), ('No Major', 'No Major')], max_length=200, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='student_pictures/')),
                ('status', models.CharField(default='Pending', max_length=10)),
            ],
        ),
    ]
