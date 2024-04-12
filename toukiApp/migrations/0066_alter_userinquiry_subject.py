# Generated by Django 4.2.5 on 2024-04-10 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0065_rename_inquiry_answertouserinquiry_user_inquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinquiry',
            name='subject',
            field=models.CharField(choices=[('0_0', 'お亡くなりになった方（被相続人）'), ('0_1', '配偶者'), ('0_2', '子供全員'), ('0_3', '各子'), ('0_4', '子の配偶者'), ('0_5', '孫'), ('0_6', '父'), ('0_7', '母'), ('0_8', '父方の祖父'), ('0_9', '父方の祖母'), ('0_10', '母方の祖父'), ('0_11', '母方の祖母'), ('0_12', '兄弟姉妹全員'), ('0_13', '各兄弟姉妹'), ('0_14', 'その他'), ('1_0', '亡くなった方の出生から死亡までの戸籍謄本'), ('1_1', '被相続人の住民票の除票又は戸籍の附票'), ('1_2', '固定資産評価証明書'), ('1_3', '登記簿謄本'), ('1_4', '不動産を取得する方の住民票又は戸籍の附票'), ('1_5', '全相続人の印鑑証明書'), ('1_6', '全相続人の全部事項証明書'), ('1_7', 'その他'), ('2_0', '被相続人情報'), ('2_1', '相続人情報'), ('2_2', '遺産分割方法'), ('2_3', '土地情報'), ('2_4', '建物情報'), ('2_5', '区分建物情報'), ('2_6', '申請情報'), ('2_7', 'その他'), ('3_0', '遺産分割協議証明書'), ('3_1', '委任状'), ('3_2', '登記申請書'), ('3_3', '相続関係説明図'), ('3_4', 'その他'), ('4_0', '取得した書類を確認する'), ('4_1', '下記書類を登記申請書（申請書）と同じ通数コピーする'), ('4_2', '下記の順番で書類を全て重ねて左側2か所をホッチキスで留めする'), ('4_3', '３でホッチキス留めした書類に記入押印等する'), ('4_4', '４まで処理した書類の後ろに書類の原本を以下の順番で重ねてクリアファイルにはさむ'), ('4_5', '法務局に書類を提出する'), ('4_6', 'その他'), ('5_0', '提出した申請書類に不備があった場合'), ('5_1', '手続が完了したら'), ('5_2', 'その他')], max_length=50, verbose_name='項目'),
        ),
    ]
