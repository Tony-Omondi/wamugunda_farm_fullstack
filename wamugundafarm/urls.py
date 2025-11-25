# wamugundafarm/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app (Home, About, Contact) - NO namespace here
    path('', include('core.urls')),                    # → http://127.0.0.1:8000/
    
    # Shop
    path('shop/', include('shop.urls')),               # → http://127.0.0.1:8000/shop/
    
    # Cart
    path('cart/', include('cart.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)