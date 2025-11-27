# core/admin.py
from django.contrib import admin
from .models import GalleryCategory, GalleryItem, Testimonial  # Add Testimonial

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'item_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'likes', 'comments', 'order', 'is_active']
    list_filter = ['category', 'content_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'subtitle']
    ordering = ['order', '-created_at']

# ADD TESTIMONIAL ADMIN
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('client_name', 'testimonial_text')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)