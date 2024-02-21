# Generated by Django 4.2.5 on 2024-02-01 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toukiApp', '0027_remove_decedent_resistry_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberOfProperties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('land', models.IntegerField(blank=True, default=0, null=True, verbose_name='土地')),
                ('house', models.IntegerField(blank=True, default=0, null=True, verbose_name='建物')),
                ('bldg', models.IntegerField(blank=True, default=0, null=True, verbose_name='区分建物')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='number_of_properties_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('decedent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='number_of_properties', to='toukiApp.decedent', verbose_name='被相続人')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='number_of_properties_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': '土地',
                'verbose_name_plural': '土地',
            },
        ),
    ]