# Generated by Django 3.2.4 on 2021-08-12 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artemis', '0002_alter_geochemistry_replicate'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Minerology',
            new_name='Mineralogy',
        ),
    ]
