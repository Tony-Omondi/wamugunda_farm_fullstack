# core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from shop.models import Product
from .models import GalleryCategory, GalleryItem, Testimonial
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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

        # ADD TESTIMONIALS
        context['testimonials'] = Testimonial.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]

        return context

def about(request):
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:5]
    context = {
        'testimonials': testimonials,
    }
    return render(request, 'about.html', context)  # ✅ Fixed - added context parameter

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

@require_POST
def submit_testimonial(request):
    client_name = request.POST.get('client_name')
    testimonial_text = request.POST.get('testimonial_text')
    
    if client_name and testimonial_text:
        testimonial = Testimonial.objects.create(
            client_name=client_name,
            testimonial_text=testimonial_text,
            is_active=False  # Requires admin approval
        )
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Please fill all fields'}, status=400)