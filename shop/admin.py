# shop/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main')

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('name', 'email', 'rating', 'comment', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'in_stock', 'is_hot', 'is_new', 'on_sale')
    list_editable = ('price', 'old_price', 'in_stock', 'is_hot', 'is_new', 'on_sale')
    list_filter = ('category', 'available', 'in_stock', 'is_hot', 'is_new', 'on_sale')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    readonly_fields = ('created', 'updated')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"