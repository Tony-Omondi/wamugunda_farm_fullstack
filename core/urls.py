# core/urls.py
from django.urls import path
from .views import HomeView, about, contact, gallery, submit_testimonial  # Add submit_testimonial

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('gallery/', gallery, name='gallery'),
    path('submit-testimonial/', submit_testimonial, name='submit_testimonial'),  # Add this line
]