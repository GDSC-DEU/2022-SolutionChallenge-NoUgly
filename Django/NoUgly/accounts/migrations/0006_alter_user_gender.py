# Generated by Django 3.2.8 on 2022-03-12 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('남', '남자'), ('여', '여자')], max_length=20),
        ),
    ]
