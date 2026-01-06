from django.contrib import admin
from .models import Order  # <--- Changed from orders.models to .models

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'full_name',
        'phone',
        'created',
        'get_total_display',
        'shipping_zone',
        'whatsapp_sent',
        'pdf_invoice'
    )
    list_filter = ('created', 'shipping_zone', 'whatsapp_sent')
    search_fields = ('order_id', 'full_name', 'email', 'phone', 'shipping_zone')
    readonly_fields = ('order_id', 'created', 'items')

    fieldsets = (
        ('Customer Details', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Order Info', {
            'fields': ('order_id', 'created', 'total_paid', 'shipping_zone', 'shipping_cost')
        }),
        ('Items', {
            'fields': ('items',),
            'description': 'JSON representation of the products ordered.'
        }),
        ('Status & Invoice', {
            'fields': ('whatsapp_sent', 'pdf_invoice'),
        }),
    )

    def get_total_display(self, obj):
        return f"KSh {obj.get_total_with_shipping()}"
    get_total_display.short_description = 'Total'