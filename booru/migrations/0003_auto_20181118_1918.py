# Generated by Django 2.1.2 on 2018-11-18 19:18

import booru.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booru', '0002_auto_20181113_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalpost',
            old_name='image',
            new_name='media',
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.AddField(
            model_name='post',
            name='media',
            field=models.FileField(blank=True, upload_to=booru.models.get_file_path_media),
        ),
    ]
