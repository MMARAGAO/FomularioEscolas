# Generated by Django 2.2.28 on 2023-08-10 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20230808_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskassessment',
            name='assesment_date_taken',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]