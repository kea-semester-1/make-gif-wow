# Generated by Django 4.2.5 on 2023-09-28 21:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mkgif", "0004_animation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="animation",
            name="job_id",
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]