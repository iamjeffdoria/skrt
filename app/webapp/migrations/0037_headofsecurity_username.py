# Generated by Django 5.0.4 on 2024-09-16 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0036_alter_userprofile_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='headofsecurity',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
