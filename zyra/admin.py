from django.contrib import admin
from .models import Catagory, Product, User, Order, OrderItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')

admin.site.register(Catagory, CategoryAdmin)
admin.site.register(Product)
admin.site.register(User)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_date', 'total_price')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
