# Generated by Django 3.1.5 on 2021-11-04 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('film', '0005_auto_20211104_1304'),
    ]

    operations = [
        migrations.RenameField(
            model_name='film',
            old_name='banner',
            new_name='banner_url',
        ),
    ]
