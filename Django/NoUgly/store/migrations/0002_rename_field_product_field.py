# Generated by Django 3.2.8 on 2022-01-25 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='Field',
            new_name='field',
        ),
    ]
