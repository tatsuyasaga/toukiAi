# Generated by Django 4.2.5 on 2024-04-09 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0061_userinquiry_answertouserinquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinquiry',
            name='category',
            field=models.CharField(choices=[('基本データ入力', 0), ('必要書類一覧', 1), ('詳細データ入力', 2), ('書類の印刷', 3), ('法務局に申請', 4), ('申請後について', 5)], max_length=50, verbose_name='進捗状況'),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='subject',
            field=models.CharField(choices=[('お亡くなりになった方（被相続人）について', '0_0'), ('配偶者について', '0_1'), ('子供全員について', '0_2'), ('各子について', '0_3'), ('子の配偶者について', '0_4'), ('孫について', '0_5'), ('父について', '0_6'), ('母について', '0_7'), ('父方の祖父について', '0_8'), ('父方の祖母について', '0_9'), ('母方の祖父について', '0_10'), ('母方の祖母について', '0_11'), ('兄弟姉妹全員について', '0_12'), ('各兄弟姉妹について', '0_13'), ('その他', '0_14'), ('亡くなった方の出生から死亡までの戸籍謄本', '1_0'), ('被相続人の住民票の除票又は戸籍の附票', '1_1'), ('固定資産評価証明書', '1_2'), ('登記簿謄本', '1_3'), ('不動産を取得する方の住民票又は戸籍の附票', '1_4'), ('全相続人の印鑑証明書', '1_5'), ('全相続人の全部事項証明書', '1_6'), ('その他', '1_7'), ('被相続人情報', '2_0'), ('相続人情報', '2_1'), ('遺産分割方法', '2_2'), ('土地情報', '2_3'), ('建物情報', '2_4'), ('区分建物情報', '2_5'), ('申請情報', '2_6'), ('その他', '2_7'), ('遺産分割協議証明書', '3_0'), ('委任状', '3_1'), ('登記申請書', '3_2'), ('相続関係説明図', '3_3'), ('その他', '3_4'), ('取得した書類を確認する', '4_0'), ('下記書類を登記申請書（申請書）と同じ通数コピーする', '4_1'), ('下記の順番で書類を全て重ねて左側2か所をホッチキスで留めする', '4_2'), ('３でホッチキス留めした書類に記入押印等する', '4_3'), ('４まで処理した書類の後ろに書類の原本を以下の順番で重ねてクリアファイルにはさむ', '4_4'), ('法務局に書類を提出する', '4_5'), ('その他', '4_6'), ('提出した申請書類に不備があった場合', '5_0'), ('手続が完了したら', '5_1'), ('その他', '5_2')], max_length=50, verbose_name='項目'),
        ),
    ]
