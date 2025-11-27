# cart/cart.py
from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # create empty cart if doesn't exist
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'quantity': 0,
            }
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity <= 0:
                self.remove(product_id)
            else:
                self.cart[product_id]['quantity'] = quantity
            self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """Safe iterator — auto-removes deleted products, never crashes template"""
        product_ids = list(self.cart.keys())
        valid_ids = [pid for pid in product_ids if pid.isdigit()]
        
        if not valid_ids:
            return  # empty cart

        products = Product.objects.filter(id__in=valid_ids)
        products_dict = {str(p.id): p for p in products}

        for product_id in product_ids:
            if product_id not in products_dict:
                # Product was deleted → silently remove from cart
                del self.cart[product_id]
                continue

            item = self.cart[product_id].copy()
            item['product'] = products_dict[product_id]
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['product_id'] = int(product_id)  # safe for url tag
            yield item

        # Save cleaned cart
        self.save()

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.session.modified = True