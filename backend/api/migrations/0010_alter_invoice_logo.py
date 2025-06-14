# Generated by Django 5.2.1 on 2025-06-05 15:29

import backend.storage_backends
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_taskstatus_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='logo',
            field=models.ImageField(blank=True, null=True, storage=backend.storage_backends.LogoStorage(), upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])]),
        ),
    ]
