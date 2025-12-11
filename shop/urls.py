# shop/urls.py
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # RECIPES
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipe/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/<slug:slug>/download-pdf/', views.recipe_pdf_download, name='recipe_pdf'),
]