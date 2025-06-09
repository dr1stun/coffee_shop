# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('product/add/', views.product_add, name='product_add'),
    path('search/', views.search_results, name='search_results'),
    path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
]