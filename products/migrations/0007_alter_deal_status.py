# Generated by Django 4.0.3 on 2022-03-29 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_deal_payment_confirmed_deal_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='status',
            field=models.CharField(choices=[('confirmed', 'confirmed'), ('pending', 'pending')], default='pending', max_length=30),
        ),
    ]
