# Generated by Django 4.2.5 on 2024-02-11 07:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('toukiApp', '0033_rename_relationship_relatedindividual_relationship'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ascendant',
            name='percentage',
        ),
        migrations.RemoveField(
            model_name='collateral',
            name='percentage',
        ),
        migrations.RemoveField(
            model_name='descendant',
            name='percentage',
        ),
        migrations.RemoveField(
            model_name='spouse',
            name='percentage',
        ),
        migrations.AddField(
            model_name='ascendant',
            name='is_acquire',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='不動産取得'),
        ),
        migrations.AddField(
            model_name='collateral',
            name='is_acquire',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='不動産取得'),
        ),
        migrations.AddField(
            model_name='descendant',
            name='is_acquire',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='不動産取得'),
        ),
        migrations.AddField(
            model_name='spouse',
            name='is_acquire',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='不動産取得'),
        ),
        migrations.CreateModel(
            name='CashAcquirer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('object_id1', models.PositiveIntegerField(blank=True, null=True, verbose_name='不動産id')),
                ('object_id2', models.PositiveIntegerField(blank=True, null=True, verbose_name='相続人id')),
                ('percentage', models.CharField(default='', max_length=100, verbose_name='取得割合')),
                ('content_type1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cash_acquirer1', to='contenttypes.contenttype', verbose_name='不動産')),
                ('content_type2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cash_acquirer2', to='contenttypes.contenttype', verbose_name='相続人')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_acquirer_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('decedent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_acquirer', to='toukiApp.decedent', verbose_name='被相続人')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_acquirer_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': '金銭の取得者',
                'verbose_name_plural': '金銭の取得者',
            },
        ),
    ]