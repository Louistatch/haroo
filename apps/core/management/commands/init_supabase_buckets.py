"""
Commande Django pour initialiser les buckets Supabase Storage.
Usage: python manage.py init_supabase_buckets
"""
from django.core.management.base import BaseCommand
from apps.core.supabase_storage import ensure_buckets_exist, BUCKETS


class Command(BaseCommand):
    help = "Crée les buckets Supabase Storage (profiles, documents, justificatifs, messaging)"

    def handle(self, *args, **options):
        self.stdout.write("Initialisation des buckets Supabase Storage...")
        try:
            ensure_buckets_exist()
            for name, opts in BUCKETS.items():
                visibility = "public" if opts['public'] else "privé"
                self.stdout.write(self.style.SUCCESS(f"  ✓ {name} ({visibility})"))
            self.stdout.write(self.style.SUCCESS("Buckets Supabase initialisés."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur: {e}"))
