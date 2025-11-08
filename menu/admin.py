from django.contrib import admin
from .models import MenuCategory, MenuItem, ExtraTopping

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'spice_level', 'customizable_spice', 'popular', 'prep_time']
    list_filter = ['category', 'spice_level', 'customizable_spice', 'popular', 'tags']
    search_fields = ['name', 'description']
    filter_horizontal = ['extra_toppings']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'category', 'description', 'detailed_description', 'price', 'image']
        }),
        ('Spice Level', {
            'fields': ['spice_level', 'customizable_spice']
        }),
        ('Details', {
            'fields': ['popular', 'prep_time', 'serves', 'ingredients', 'tags']
        }),
        ('Nutrition', {
            'fields': ['calories', 'protein', 'carbs', 'fat', 'rating']
        }),
        ('Extras', {
            'fields': ['extra_toppings']
        }),
    ]

@admin.register(ExtraTopping)
class ExtraToppingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']