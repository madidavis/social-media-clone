# Generated by Django 4.1.6 on 2023-02-20 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialnetwork', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='input_text',
            new_name='post_input_text',
        ),
    ]
