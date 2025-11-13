from django.db import models

class MenuCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Add this if missing
    updated_at = models.DateTimeField(auto_now=True)      # Add this if missing

    def __str__(self):
        return self.name

    # REMOVE the item_count property - we'll use annotation instead
    # @property
    # def item_count(self):
    #     return self.items.count()

class ExtraTopping(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    SPICE_LEVEL_CHOICES = [
        ('mild', 'Mild'),
        ('medium', 'Medium'), 
        ('hot', 'Hot'),
        ('extra_hot', 'Extra Hot'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    detailed_description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    popular = models.BooleanField(default=False)
    prep_time = models.CharField(max_length=50)
    serves = models.CharField(max_length=50)
    ingredients = models.JSONField(default=list)
    calories = models.CharField(max_length=50)
    protein = models.CharField(max_length=50)
    carbs = models.CharField(max_length=50)
    fat = models.CharField(max_length=50)
    rating = models.CharField(max_length=10)
    tags = models.JSONField(default=list)
    
    # Spice Level Fields
    spice_level = models.CharField(
        max_length=20,
        choices=SPICE_LEVEL_CHOICES,
        default='mild'
    )
    customizable_spice = models.BooleanField(default=True)
    
    # Relationships
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    extra_toppings = models.ManyToManyField(ExtraTopping, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']