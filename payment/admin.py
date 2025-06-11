from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

# Create order items inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
   
# Extend our order model to include order items
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = [
        "user",
        "full_name",
        "email",
        "shipping_address",
        "amount_paid",
        "date_ordered",
        "shipped",
        "date_shipped",
        "invoice",
        "paid",
    ]
    inlines = [OrderItemInline]


# Unregister the order model
admin.site.unregister(Order)

# Register the new order model with the order items inline
admin.site.register(Order, OrderAdmin)