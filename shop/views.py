# shop/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category


# Shop main page → /shop/
class ShopListView(ListView):
    model = Product
    template_name = 'shop/shop_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(available=True).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# Category page → /shop/category/fruits/
class CategoryDetailView(ListView):
    model = Product
    template_name = 'shop/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category, available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# Product detail → /shop/product/bosco-apple/
class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['main_image'] = product.images.filter(is_main=True).first() or product.images.first()
        context['gallery_images'] = product.images.all()
        context['reviews'] = product.reviews.filter(is_approved=True)
        context['related_products'] = Product.objects.filter(
            category=product.category, available=True
        ).exclude(id=product.id)[:8]
        return context