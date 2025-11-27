# core/models.py
from django.db import models

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class GalleryItem(models.Model):
    CONTENT_TYPES = [
        ('reel', 'Reel'),
        ('post', 'Post'),
        ('story', 'Story'),
    ]
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100, blank=True)
    instagram_url = models.URLField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='post')
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
    
    # Engagement metrics (optional - can be manually updated or automated via API)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    
    # Ordering and visibility
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_instagram_embed_id(self):
        """Extract Instagram post ID from URL for embedding"""
        if '/reel/' in self.instagram_url:
            return self.instagram_url.split('/reel/')[-1].strip('/')
        elif '/p/' in self.instagram_url:
            return self.instagram_url.split('/p/')[-1].strip('/')
        return None