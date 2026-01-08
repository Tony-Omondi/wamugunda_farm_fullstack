from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from shop.models import Product
from .models import GalleryCategory, GalleryItem, Testimonial
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

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
    return render(request, 'about.html', context)

def contact(request):
    if request.method == "POST":
        # 1. Get data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # 2. Format the email content
        email_subject = f"Website Contact: {subject}"
        email_message = f"""
        You have received a new message from the Wamugunda Farm website.

        --------------------------------
        DETAILS:
        Name:    {name}
        Email:   {email}
        Phone:   {phone}
        Subject: {subject}
        --------------------------------
        
        MESSAGE:
        {message}
        """

        # 3. Send the email
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.EMAIL_HOST_USER, # Sends from orders@wamugundafarm.co.ke
                recipient_list=[settings.EMAIL_HOST_USER, 'info.douglas@wamugundafarm.co.ke'], # Sends to both
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
            
        except Exception as e:
            print(f"Error sending email: {e}")
            messages.error(request, "Error sending message. Please try again or WhatsApp us.")

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