# Generated by Django 5.1.6 on 2025-02-13 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_userprofile_is_moderator'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_affiliated',
            field=models.BooleanField(default=False),
        ),
    ]
