from django.urls import path
from .views import HomeView, about, contact

# app_name = 'core'   # THIS MUST BE HERE

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('gallery/', contact, name='gallery'),
]