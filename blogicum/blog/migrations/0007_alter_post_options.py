# Generated by Django 3.2.16 on 2023-11-26 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_rename_comment_comment_post'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date', 'id'), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
