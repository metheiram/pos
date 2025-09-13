from django.contrib import admin
from .models import Category, MenuItem, Table, Order, OrderItem, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'created_at']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'status', 'created_at']
    list_filter = ['status', 'seats']
    list_editable = ['status']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total']
    
    def get_total(self, obj):
        return f"${obj.get_total()}" if obj.id else "-"
    get_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'table', 'customer_name', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at', 'table']
    search_fields = ['order_number', 'customer_name']
    readonly_fields = ['order_number', 'subtotal', 'tax_amount', 'total']
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'method', 'processed_by', 'processed_at']
    list_filter = ['method', 'processed_at']
    readonly_fields = ['processed_at']