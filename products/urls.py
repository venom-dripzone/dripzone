
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart',
    ),
    path('cart/', views.cart, name='cart'),
    path(
        'cart/update/<int:product_id>/',
        views.update_cart,
        name='update_cart',
    ),
    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart',
    ),
]
