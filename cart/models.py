# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  # This becomes 316, 317...
    created = models.DateTimeField(auto_now_add=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_zone = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    items = models.JSONField()  # Stores cart items
    whatsapp_sent = models.BooleanField(default=False)
    pdf_invoice = models.FileField(upload_to='invoices/', null=True, blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Order #{self.order_id}"

    def get_total_with_shipping(self):
        return self.total_paid + self.shipping_cost