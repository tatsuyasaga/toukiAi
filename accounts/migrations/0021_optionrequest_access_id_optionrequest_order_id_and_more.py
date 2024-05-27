# Generated by Django 4.2.5 on 2024-05-25 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_optionrequest_is_card_alter_optionrequest_payer'),
    ]

    operations = [
        migrations.AddField(
            model_name='optionrequest',
            name='access_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='取引ID'),
        ),
        migrations.AddField(
            model_name='optionrequest',
            name='order_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='オーダーID'),
        ),
        migrations.AddField(
            model_name='optionrequest',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='トランザクションID'),
        ),
    ]