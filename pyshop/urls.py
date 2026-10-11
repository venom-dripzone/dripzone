from django.contrib import admin
from django.urls import path, include
from products import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('checkout/', views.checkout, name='checkout'),
]