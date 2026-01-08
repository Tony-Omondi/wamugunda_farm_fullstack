# core/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import GalleryCategory, GalleryItem, Testimonial

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'order', 'item_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    
    @display(description='Items')
    def item_count(self, obj):
        return obj.items.count()

@admin.register(GalleryItem)
class GalleryItemAdmin(ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'likes', 'comments', 'order', 'is_active']
    list_filter = ['category', 'content_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'subtitle']
    ordering = ['order', '-created_at']

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('client_name', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('client_name', 'testimonial_text')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)