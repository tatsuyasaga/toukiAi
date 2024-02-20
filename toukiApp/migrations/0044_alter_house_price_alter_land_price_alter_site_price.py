# Generated by Django 4.2.5 on 2024-02-18 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0043_house_house_number_land_land_number_alter_land_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='price',
            field=models.CharField(default='', max_length=13, verbose_name='固定資産評価額'),
        ),
        migrations.AlterField(
            model_name='land',
            name='price',
            field=models.CharField(default='', max_length=13, verbose_name='固定資産評価額'),
        ),
        migrations.AlterField(
            model_name='site',
            name='price',
            field=models.CharField(default='', max_length=13, verbose_name='固定資産評価額'),
        ),
    ]
