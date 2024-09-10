# Generated by Django 5.0.4 on 2024-07-14 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0015_alter_studrec_major'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studrec',
            name='major',
            field=models.CharField(blank=True, choices=[('English', 'English'), ('Filipino', 'Filipino'), ('Mathematics', 'Mathematics'), ('Social Studies', 'Social Studies'), ('Automative', 'Automative'), ('Drafting', 'Drafting'), ('Electrical', 'Electrical'), ('Electronics', 'Electronics'), ('Fashion and Apparel', 'Fashion and Apparel'), ('Food and Beverages Preparation Service Management', 'Food and Beverages Preparation Service Management'), ('Mechanical', 'Mechanical'), ('Powerplant', 'Powerplant'), ('Heating, Ventilating, Air-conditioning & Refrigeration', 'Heating, Ventilating, Air-conditioning & Refrigeration'), ('Welding and Fabrication', 'Welding and Fabrication'), ('No Major', 'No Major')], max_length=200, null=True),
        ),
    ]
