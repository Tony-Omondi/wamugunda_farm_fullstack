from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'created',
        'total_paid',
        'shipping_zone',
        'shipping_cost',
        'whatsapp_sent',
    )
    list_filter = ('created', 'shipping_zone', 'whatsapp_sent')
    search_fields = ('order_id', 'shipping_zone')
    readonly_fields = ('order_id', 'created')

    fieldsets = (
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
