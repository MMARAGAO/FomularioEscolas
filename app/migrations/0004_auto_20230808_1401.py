# Generated by Django 2.2.28 on 2023-08-08 17:01

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_auto_20230720_1107'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userresponse',
            unique_together={('user', 'risk_factor')},
        ),
    ]
