"""
Django management command: python manage.py seed_data
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crée les données de démonstration pour TaskManager Pro'

    def handle(self, *args, **options):
        from seed_data import create_demo_data
        create_demo_data()
