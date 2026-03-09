# Generated manually for TASK-6: Performance Optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_photo_profil'),
    ]

    operations = [
        # Index sur User
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='idx_user_email'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['phone_number'], name='idx_user_phone'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['user_type'], name='idx_user_type'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_active'], name='idx_user_active'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['-created_at'], name='idx_user_created'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['user_type', 'is_active'], name='idx_user_type_active'),
        ),

        # Index sur AgronomeProfile (vrais noms de champs)
        migrations.AddIndex(
            model_name='agronomeprofile',
            index=models.Index(fields=['statut_validation'], name='idx_agro_validated'),
        ),

        # Index sur ExploitantProfile (vrais noms de champs)
        migrations.AddIndex(
            model_name='exploitantprofile',
            index=models.Index(fields=['statut_verification'], name='idx_expl_verified'),
        ),

        # Index sur DocumentJustificatif (vrais noms de champs)
        migrations.AddIndex(
            model_name='documentjustificatif',
            index=models.Index(fields=['type_document'], name='idx_doc_type'),
        ),
        migrations.AddIndex(
            model_name='documentjustificatif',
            index=models.Index(fields=['agronome_profile', 'type_document'], name='idx_doc_user_type'),
        ),

        # Index sur FarmVerificationDocument (vrais noms de champs)
        migrations.AddIndex(
            model_name='farmverificationdocument',
            index=models.Index(fields=['exploitant_profile'], name='idx_farm_user'),
        ),
    ]
