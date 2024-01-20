# Generated by Django 4.2.5 on 2023-12-18 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toukiApp', '0016_alter_decedent_domicile_prefecture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ascendant',
            name='prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='住所の都道府県'),
        ),
        migrations.AlterField(
            model_name='collateral',
            name='prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='住所の都道府県'),
        ),
        migrations.AlterField(
            model_name='decedent',
            name='domicile_prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='本籍地の都道府県'),
        ),
        migrations.AlterField(
            model_name='decedent',
            name='prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='住所の都道府県'),
        ),
        migrations.AlterField(
            model_name='decedent',
            name='resistry_prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='登記上の都道府県'),
        ),
        migrations.AlterField(
            model_name='descendant',
            name='prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='住所の都道府県'),
        ),
        migrations.AlterField(
            model_name='spouse',
            name='prefecture',
            field=models.CharField(choices=[('', '選択してください'), ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'), ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'), ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県')], default=None, max_length=20, null=True, verbose_name='住所の都道府県'),
        ),
        migrations.CreateModel(
            name='DescendantCommon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('is_exist', models.BooleanField(blank=True, default=None, null=True, verbose_name='死亡時存在')),
                ('count', models.IntegerField(default=0, verbose_name='子の数')),
                ('is_same_paremts', models.BooleanField(blank=True, default=None, null=True, verbose_name='同じ両親')),
                ('is_live', models.BooleanField(blank=True, default=None, null=True, verbose_name='手続時存在')),
                ('is_refuse', models.BooleanField(blank=True, default=None, null=True, verbose_name='相続放棄')),
                ('is_adult', models.BooleanField(blank=True, default=None, null=True, verbose_name='成人')),
                ('is_japan', models.BooleanField(blank=True, default=None, null=True, verbose_name='日本在住')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descendant_common_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('decedent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descendant_common', to='toukiApp.decedent', verbose_name='被相続人')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descendant_common_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': '卑属共通',
                'verbose_name_plural': '卑属共通',
            },
        ),
        migrations.CreateModel(
            name='CollateralCommon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('is_exist', models.BooleanField(blank=True, default=None, null=True, verbose_name='死亡時存在')),
                ('count', models.IntegerField(default=0, verbose_name='子の数')),
                ('is_same_paremts', models.BooleanField(blank=True, default=None, null=True, verbose_name='同じ両親')),
                ('is_live', models.BooleanField(blank=True, default=None, null=True, verbose_name='手続時存在')),
                ('is_refuse', models.BooleanField(blank=True, default=None, null=True, verbose_name='相続放棄')),
                ('is_adult', models.BooleanField(blank=True, default=None, null=True, verbose_name='成人')),
                ('is_japan', models.BooleanField(blank=True, default=None, null=True, verbose_name='日本在住')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collateral_common_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('decedent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collateral_common', to='toukiApp.decedent', verbose_name='被相続人')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collateral_common_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': '傍系共通',
                'verbose_name_plural': '傍系共通',
            },
        ),
    ]