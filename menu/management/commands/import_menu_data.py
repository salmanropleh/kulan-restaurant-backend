from django.core.management.base import BaseCommand
from menu.models import MenuCategory, MenuItem, ExtraTopping

class Command(BaseCommand):
    help = 'Import menu data from React structure'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Menu data import command ready'))
        # We'll add the actual import logic later