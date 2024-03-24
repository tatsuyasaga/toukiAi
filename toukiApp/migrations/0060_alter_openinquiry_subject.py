# Generated by Django 4.2.5 on 2024-03-22 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0059_alter_bldg_register_alter_house_register_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinquiry',
            name='subject',
            field=models.CharField(choices=[('システム詳細', 'システム詳細'), ('料金', '料金'), ('オプション', 'オプション'), ('提携司法書士', '提携司法書士'), ('運営者', '運営者'), ('その他', 'その他')], max_length=20, verbose_name='件名'),
        ),
    ]