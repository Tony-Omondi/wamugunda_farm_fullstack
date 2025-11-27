# shop/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg, Count
from .models import Product, Category

class ShopListView(ListView):
    model = Product
    template_name = 'shop/shop_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Sorting
        order_by = self.request.GET.get('orderby', 'latest')
        if order_by == 'price':
            queryset = queryset.order_by('price')
        elif order_by == 'price-desc':
            queryset = queryset.order_by('-price')
        elif order_by == 'rating':
            # Annotate with average rating and order by it
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        else:  # latest
            queryset = queryset.order_by('-created')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

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
        context['categories'] = Category.objects.all()
        return context

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