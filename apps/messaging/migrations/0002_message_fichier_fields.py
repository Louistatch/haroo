from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='fichier',
            field=models.FileField(blank=True, null=True, upload_to='messages/fichiers/%Y/%m/', verbose_name='Fichier joint'),
        ),
        migrations.AddField(
            model_name='message',
            name='nom_fichier',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Nom du fichier'),
        ),
        migrations.AddField(
            model_name='message',
            name='taille_fichier',
            field=models.IntegerField(default=0, verbose_name='Taille du fichier (octets)'),
        ),
        migrations.AddField(
            model_name='message',
            name='motif_signalement',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Motif du signalement'),
        ),
        migrations.AlterField(
            model_name='message',
            name='contenu',
            field=models.TextField(blank=True, default='', verbose_name='Contenu'),
        ),
    ]
