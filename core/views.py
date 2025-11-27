# core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from shop.models import Product
from .models import GalleryCategory, GalleryItem

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FEATURED PRODUCTS
        context['featured_products'] = Product.objects.filter(
            available=True
        ).select_related('category').prefetch_related('images').order_by('-created')[:12]

        context['hot_products'] = Product.objects.filter(
            available=True, is_hot=True
        )[:8]

        context['new_products'] = Product.objects.filter(
            available=True, is_new=True
        )[:8]

        return context

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def gallery(request):
    # Get all active categories with their items
    categories = GalleryCategory.objects.prefetch_related(
        'items'
    ).filter(
        items__is_active=True
    ).distinct()
    
    # Get all gallery items for the main display
    gallery_items = GalleryItem.objects.filter(
        is_active=True
    ).select_related('category').order_by('order', '-created_at')
    
    context = {
        'categories': categories,
        'gallery_items': gallery_items,
    }
    
    return render(request, 'gallery.html', context)