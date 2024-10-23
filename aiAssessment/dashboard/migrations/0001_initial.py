# Generated by Django 5.1.2 on 2024-10-22 16:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Report",
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
                ("email", models.EmailField(max_length=254)),
                ("website_url", models.URLField()),
                ("report_type", models.CharField(max_length=100)),
                ("report_content", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "userId",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("endpoint", models.CharField(max_length=255)),
                ("detailed", models.BooleanField(default=False)),
                (
                    "jobState",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("error", "Error"),
                            ("expired", "Expired"),
                            ("active", "Active"),
                            ("waiting", "Waiting"),
                        ],
                        default="waiting",
                        max_length=50,
                    ),
                ),
                ("timeStamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "taskId",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("agentId", models.CharField(max_length=255)),
                ("command", models.CharField(max_length=255)),
                ("output", models.TextField(blank=True, null=True)),
                ("error", models.TextField(blank=True, null=True)),
                ("errorCounter", models.IntegerField(default=0)),
                (
                    "taskStatus",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("error", "Error"),
                            ("expired", "Expired"),
                            ("active", "Active"),
                        ],
                        default="active",
                        max_length=50,
                    ),
                ),
                ("hasMessageBeenSent", models.BooleanField(default=False)),
                ("updateTimeStamp", models.DateTimeField(auto_now=True)),
                (
                    "userId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="dashboard.user"
                    ),
                ),
            ],
        ),
    ]