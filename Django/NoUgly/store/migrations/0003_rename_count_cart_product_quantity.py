# Generated by Django 3.2.8 on 2022-02-14 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20220214_1617'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart_product',
            old_name='count',
            new_name='quantity',
        ),
    ]
