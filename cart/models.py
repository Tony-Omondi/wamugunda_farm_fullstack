from django.db import models
from shop.models import Product

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # --- CUSTOMER DETAILS ---
    full_name = models.CharField(max_length=100, default="Guest")
    email = models.EmailField(default="noreply@example.com")
    phone = models.CharField(max_length=20, default="0000000000")
    # ------------------------

    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_zone = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Stores cart items as JSON
    items = models.JSONField() 
    
    whatsapp_sent = models.BooleanField(default=False)
    pdf_invoice = models.FileField(upload_to='invoices/', null=True, blank=True)

    class Meta:
        ordering = ['-created']
        # This helps Django Admin know where this model belongs
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_id} - {self.full_name}"

    def get_total_with_shipping(self):
        return self.total_paid + self.shipping_cost