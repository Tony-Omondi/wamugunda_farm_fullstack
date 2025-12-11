# shop/models.py
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    
    # Descriptions
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField()

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Stock & Visibility
    available = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    # Badges
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        indexes = [models.Index(fields=['-created']), models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def average_rating(self):
        return self.reviews.aggregate(avg=models.Avg('rating'))['avg'] or 5.0

    def review_count(self):
        return self.reviews.count()


# Multiple Images
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - Image"


# Fake Reviews (No login needed — just seed them)
class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Customer name
    email = models.EmailField(blank=True)
    comment = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.name} - {self.product.name} - {self.rating} stars"
    

# shop/models.py  ← add this at the very end of the file

def recipe_image_path(instance, filename):
    return f'recipes/{instance.slug}/{filename}'

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    image = models.ImageField(upload_to=recipe_image_path, help_text="Main recipe photo")
    description = models.TextField(blank=True)
    instructions = models.TextField(help_text="Step-by-step instructions")

    prep_time = models.PositiveIntegerField(default=15, help_text="In minutes")
    cook_time = models.PositiveIntegerField(default=30, help_text="In minutes")
    servings = models.PositiveIntegerField(default=4)

    difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )

    # Connect to shop products
    featured_products = models.ManyToManyField('Product', related_name='featured_in_recipes', blank=True)
    ingredients = models.ManyToManyField('Product', through='RecipeIngredient', related_name='used_in_recipes', blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = "Recipes"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:recipe_detail', args=[self.slug])


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100, blank=True, help_text="e.g. 500g, 2 cups, 1 bunch")
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('recipe', 'product')
        verbose_name = "Recipe Ingredient"

    def __str__(self):
        return f"{self.quantity} {self.product.name} → {self.recipe.title}"