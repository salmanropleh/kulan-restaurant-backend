from django.db import migrations

def populate_categories(apps, schema_editor):
    MenuCategory = apps.get_model('menu', 'MenuCategory')
    
    categories = [
        {"id": "breakfast", "name": "Breakfast", "description": "Start your day with traditional flavors"},
        {"id": "lunch", "name": "Lunch", "description": "Hearty midday meals"},
        {"id": "dinner", "name": "Dinner", "description": "Evening feasts and special dishes"},
        {"id": "afternoon", "name": "Afternoon Tea", "description": "Light bites and beverages"},
        {"id": "desserts", "name": "Desserts", "description": "Sweet endings to your meal"},
        {"id": "specials", "name": "KULAN Specialties", "description": "Our signature creations"},
        {"id": "beverages", "name": "Beverages", "description": "Traditional drinks and more"},
    ]
    
    for category_data in categories:
        MenuCategory.objects.create(**category_data)

def reverse_populate(apps, schema_editor):
    MenuCategory = apps.get_model('menu', 'MenuCategory')
    MenuCategory.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('menu', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(populate_categories, reverse_populate),
    ]