# Generated by Django 4.2.5 on 2024-02-08 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toukiApp', '0032_alter_ascendant_birth_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='relatedindividual',
            old_name='Relationship',
            new_name='relationship',
        ),
    ]