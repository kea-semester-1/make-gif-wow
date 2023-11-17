# Generated by Django 4.2.5 on 2023-11-16 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mkgif", "0005_animation_job_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("job_id", models.UUIDField()),
                ("file_path", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=10)),
                ("file_token", models.UUIDField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name="YouTubeVideo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("youtube_url", models.URLField(max_length=1024)),
                ("start_time", models.CharField(max_length=10)),
                ("end_time", models.CharField(max_length=10)),
                ("video_name", models.CharField(max_length=100)),
            ],
        ),
    ]
