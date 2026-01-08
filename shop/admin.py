from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline  # Import Unfold classes
from unfold.decorators import display               # Import Unfold display decorator
from .models import (
    Category,
    Product,
    ProductImage,
    Review,
    Recipe,
    RecipeIngredient
)


# ==================== INLINES ====================

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main')


class ReviewInline(TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('name', 'email', 'rating', 'comment', 'created_at')


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['product']
    fields = ('product', 'quantity', 'notes')


# ==================== ADMIN CLASSES ====================

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'in_stock', 'is_hot', 'is_new', 'on_sale', 'created')
    list_editable = ('price', 'old_price', 'in_stock', 'is_hot', 'is_new', 'on_sale')
    list_filter = ('category', 'available', 'in_stock', 'is_hot', 'is_new', 'on_sale', 'created')
    search_fields = ('name', 'short_description', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at', 'product__category')
    search_fields = ('name', 'product__name', 'comment')
    readonly_fields = ('created_at',)
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('thumbnail', 'title', 'difficulty', 'prep_time', 'cook_time', 'servings', 'is_active', 'created_at')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'instructions')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)
    filter_horizontal = ('featured_products',)
    inlines = [RecipeIngredientInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'image', 'description')
        }),
        ('Cooking Details', {
            'fields': (('prep_time', 'cook_time', 'servings'), 'difficulty')
        }),
        ('Promoted Products', {
            'fields': ('featured_products',),
            'description': 'Products to highlight/promote in this recipe (e.g. special tools, premium items)'
        }),
        ('Instructions', {
            'fields': ('instructions',),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    # Using Unfold's @display decorator for the image preview
    @display(description="Preview")
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px; height:60px; object-fit:cover; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">',
                obj.image.url
            )
        return "(No image)"