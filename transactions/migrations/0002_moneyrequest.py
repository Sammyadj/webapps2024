# Generated by Django 5.0.3 on 2024-03-30 19:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_requested', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')], max_length=3)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('DECLINED', 'Declined')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('requested_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='money_requests_received', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='money_requests_made', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]