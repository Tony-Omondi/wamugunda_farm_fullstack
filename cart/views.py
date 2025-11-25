# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from shop.models import Product
from .cart import Cart


# Delivery Zones & Costs
SHIPPING_ZONES = {
    'Thika Road': 250,
    'Garden Estate': 250,
    'Runda': 300,
    'Muthaiga': 300,
    'Ruaka': 250,
    'Thendegua': 250,
    'Parklands': 250,
    'Westlands': 250,
    'Redhill Road': 400,
    'Sarit Center': 300,
    'Waiyaki Way': 300,
}


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(str(product_id))
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request):
    cart = Cart(request)
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            product_id = key.split('_')[1]
            try:
                qty = int(value)
                if qty > 0:
                    cart.update(product_id, qty)
                else:
                    cart.remove(product_id)
            except ValueError:
                pass

    messages.success(request, 'Cart updated!')
    return redirect('cart:cart_detail')


@require_POST
def set_shipping_zone(request):
    zone = request.POST.get('shipping_zone')

    if zone in SHIPPING_ZONES:
        request.session['shipping_zone'] = zone
        messages.success(request, f"Delivery zone set: {zone} (+KSh {SHIPPING_ZONES[zone]})")
    else:
        request.session.pop('shipping_zone', None)
        messages.info(request, "Delivery zone cleared.")

    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)

    # Shipping logic
    selected_zone = request.session.get('shipping_zone')
    shipping_cost = SHIPPING_ZONES.get(selected_zone, 0)

    # Build WhatsApp items list
    items = []
    for item in cart:
        items.append(f"• {item['quantity']}x {item['product'].name} - KSh {item['total_price']}")

    whatsapp_items = "\n".join(items) if items else "No items"
    total = cart.get_total_price() + shipping_cost

    # Clean WhatsApp message (NO %0A)
    whatsapp_message = (
        "Hello Wamugunda Farm!\n\n"
        "🧺 *My Order:*\n"
        f"{whatsapp_items}\n\n"
        f"📍 *Delivery Zone:* {selected_zone or 'Not selected'}\n"
        f"🚚 *Shipping:* KSh {shipping_cost}\n"
        f"💰 *Total Amount:* KSh {total}\n\n"
        "Thank you for recieving my order! 🙏"
    )

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'shipping_zones': SHIPPING_ZONES,
        'selected_zone': selected_zone,
        'shipping_cost': shipping_cost,
        'whatsapp_message': whatsapp_message,
    })
