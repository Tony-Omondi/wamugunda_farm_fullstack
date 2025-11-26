# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/', views.cart_update, name='cart_update'),
    path('set-shipping/', views.set_shipping_zone, name='set_shipping_zone'),
    
    # THIS LINE WAS MISSING — ADD IT NOW!!!
    path('create-whatsapp-order/', views.create_whatsapp_order, name='create_whatsapp_order'),
]