# Generated by Django 3.1.7 on 2021-04-16 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyflow', '0007_commentlike_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
