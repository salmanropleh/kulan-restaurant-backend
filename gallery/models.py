from django.db import models

class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('interior', 'Interior'),
        ('experience', 'Experience'),
        ('events', 'Events'),
        ('chef', 'Chef Specials'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='gallery/images/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='food')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Order in which images are displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return self.title