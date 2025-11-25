# core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from shop.models import Product


class HomeView(TemplateView):
    template_name = 'home.html'  # or just 'home.html' if your template is in root/templates

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # FEATURED PRODUCTS — Latest 12 fresh & available products
        context['featured_products'] = Product.objects.filter(
            available=True
        ).select_related('category').prefetch_related('images').order_by('-created')[:12]

        # OPTIONAL: You can also add hot/new/sale products
        context['hot_products'] = Product.objects.filter(
            available=True, is_hot=True
        )[:8]

        context['new_products'] = Product.objects.filter(
            available=True, is_new=True
        )[:8]

        return context


# Simple function views
def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')