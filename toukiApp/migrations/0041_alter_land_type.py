# Generated by Django 4.2.5 on 2024-02-14 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0040_alter_numberofproperties_bldg_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='land',
            name='type',
            field=models.CharField(blank=True, choices=[(1, '宅地'), (2, '田'), (3, '畑'), (4, '雑種地'), (5, '公衆用道路'), (6, '原野'), (7, '山林'), (8, '保安林'), (9, '墓地'), (10, '境内地'), (11, '牧場'), (12, '塩田'), (13, '鉱泉地'), (14, '池沼'), (15, '運河用地'), (16, '水道用地'), (17, '用悪水路'), (18, 'ため池'), (19, '堤'), (20, '井溝'), (21, '公園'), (22, '鉄道用地'), (23, '学校用地')], default='', max_length=100, null=True, verbose_name='地目'),
        ),
    ]