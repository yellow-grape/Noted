# Generated by Django 5.1.3 on 2024-11-22 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="public",
            field=models.BooleanField(default=False),
        ),
    ]
