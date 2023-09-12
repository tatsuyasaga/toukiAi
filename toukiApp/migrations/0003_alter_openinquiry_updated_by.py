# Generated by Django 4.2.5 on 2023-09-12 09:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toukiApp', '0002_openinquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinquiry',
            name='updated_by',
            field=models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, related_name='open_inquiry_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='最終回答者'),
        ),
    ]
