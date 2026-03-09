"""
Migration: Ajout du champ email_verified au modèle User
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_phone_number_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False, verbose_name='Email vérifié'),
        ),
    ]
