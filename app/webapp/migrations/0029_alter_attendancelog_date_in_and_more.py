# Generated by Django 5.0.4 on 2024-08-17 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0028_alter_userprofile_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelog',
            name='date_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='date_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
