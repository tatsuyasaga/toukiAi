# Generated by Django 4.2.5 on 2024-02-11 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0038_rename_all_cash_acquirer_typeofdivision_all_cash_acquirer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='typeofdivision',
            name='cash_allocation',
            field=models.CharField(blank=True, choices=[('全て一人', '全て一人'), ('全て法定相続', '全て法定相続'), ('その他', 'その他')], max_length=30, null=True, verbose_name='換価した金銭の分配方法'),
        ),
        migrations.AlterField(
            model_name='typeofdivision',
            name='property_allocation',
            field=models.CharField(blank=True, choices=[('全て一人', '全て一人'), ('全て法定相続', '全て法定相続'), ('その他', 'その他')], max_length=30, null=True, verbose_name='不動産の分配方法'),
        ),
    ]