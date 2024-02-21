# Generated by Django 4.2.5 on 2024-02-01 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toukiApp', '0026_alter_decedent_domicile_prefecture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decedent',
            name='resistry_address',
        ),
        migrations.RemoveField(
            model_name='decedent',
            name='resistry_bldg',
        ),
        migrations.RemoveField(
            model_name='decedent',
            name='resistry_city',
        ),
        migrations.RemoveField(
            model_name='decedent',
            name='resistry_prefecture',
        ),
        migrations.CreateModel(
            name='RegistryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('prefecture', models.CharField(blank=True, choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='登記上の都道府県')),
                ('city', models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='登記上の市区町村')),
                ('address', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='登記上の町域・番地')),
                ('bldg', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='登記上の建物')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registry_address_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('decedent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registry_address', to='toukiApp.decedent', verbose_name='被相続人')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registry_address_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': '登記簿上の住所',
                'verbose_name_plural': '登記簿上の住所',
            },
        ),
    ]