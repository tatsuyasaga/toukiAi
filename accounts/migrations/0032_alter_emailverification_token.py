# Generated by Django 4.2.5 on 2024-06-06 07:00

import common.validations
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_alter_emailverification_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverification',
            name='token',
            field=models.PositiveIntegerField(validators=[common.validations.validate_four_digit_number], verbose_name='トークン'),
        ),
    ]