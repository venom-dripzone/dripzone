
from django.contrib import admin
from .models import Product, Offer, Order, OrderItem


class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')



class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('category', 'price', 'stock')



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity')
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'phone',
        'total',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone', 'address')
    list_editable = ('status',)
    readonly_fields = ('total', 'created_at')
    inlines = [OrderItemInline]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity')
    search_fields = ('product_name', 'order__customer_name')
    readonly_fields = ('order', 'product', 'product_name', 'price', 'quantity')


admin.site.register(Product, ProductAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
