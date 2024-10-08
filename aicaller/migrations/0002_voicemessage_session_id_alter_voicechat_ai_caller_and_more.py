# Generated by Django 5.0.7 on 2024-07-17 11:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aicaller", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="voicemessage",
            name="session_id",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="voicechat",
            name="ai_caller",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="voicechat",
            name="duration_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="voicechat",
            name="end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
