# Generated by Django 3.2.16 on 2023-11-26 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_post_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created_at',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
