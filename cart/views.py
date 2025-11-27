# cart/views.py — FINAL VERSION (AJAX + WhatsApp + PDF + Shipping)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.files import File
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from shop.models import Product
from .cart import Cart
from cart.models import Order  # Your Order model
from urllib.parse import quote


SHIPPING_ZONES = {
    'Thika Road': 250, 'Garden Estate': 250, 'Runda': 300, 'Muthaiga': 300,
    'Ruaka': 250, 'Thendegua': 250, 'Parklands': 250, 'Westlands': 250,
    'Redhill Road': 400, 'Sarit Center': 300, 'Waiyaki Way': 300,
}

# AJAX ADD TO CART — MAIN FIX (NO PAGE RELOAD!)
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Get quantity (default 1)
    quantity = int(request.POST.get('quantity', 1))
    
    # Add to cart
    cart.add(product=product, quantity=quantity)

    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart!',
            'cart_total': len(cart),
            'cart_price': float(cart.get_total_price())
        })

    # Normal form submission (fallback)
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(str(product_id))
    messages.success(request, 'Item removed.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request):
    cart = Cart(request)
    updated = False
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            product_id = key.split('_')[1]
            try:
                qty = int(value)
                if qty > 0:
                    cart.update(product_id, qty)
                else:
                    cart.remove(product_id)
                updated = True
            except ValueError:
                pass
    if updated:
        messages.success(request, 'Cart updated!')
    return redirect('cart:cart_detail')


@require_POST
def set_shipping_zone(request):
    zone = request.POST.get('shipping_zone')
    if zone in SHIPPING_ZONES:
        request.session['shipping_zone'] = zone
        messages.success(request, f"Delivery: {zone} (+KSh {SHIPPING_ZONES[zone]})")
    else:
        request.session.pop('shipping_zone', None)
        messages.info(request, "Delivery zone cleared.")
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    selected_zone = request.session.get('shipping_zone')
    shipping_cost = SHIPPING_ZONES.get(selected_zone, 0)
    total = cart.get_total_price() + shipping_cost

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'shipping_zones': SHIPPING_ZONES,
        'selected_zone': selected_zone,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total
    })


@require_POST
def create_whatsapp_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    selected_zone = request.session.get('shipping_zone', 'Not selected')
    shipping_cost = SHIPPING_ZONES.get(selected_zone, 0)
    total = cart.get_total_price() + shipping_cost

    # Save order to DB
    order = Order.objects.create(
        total_paid=cart.get_total_price(),
        shipping_zone=selected_zone,
        shipping_cost=shipping_cost,
        items=[{
            'name': item['product'].name,
            'quantity': item['quantity'],
            'price': str(item['price']),
            'total': str(item['total_price'])
        } for item in cart]
    )

    # Generate PDF Invoice
    context = {
        'order': order,
        'cart': cart,
        'shipping_zone': selected_zone,
        'shipping_cost': shipping_cost,
        'total': total,
        'date': datetime.now().strftime('%d/%m/%Y'),
    }
    html = render_to_string('cart/invoice_pdf.html', context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    
    if not pdf.err:
        pdf_file = BytesIO(result.getvalue())
        order.pdf_invoice.save(f'invoice_{order.order_id}.pdf', File(pdf_file))
        order.save()

    # Build the plain text message first
    items_text = "\n".join([
        f"• {item['quantity']} × {item['product'].name} = KSh {item['total_price']}"
        for item in cart
    ])

    plain_message = f"""NEW ORDER #{order.order_id}

Date: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}

Items:
{items_text}

Delivery Zone: {selected_zone}
Delivery Fee: KSh {shipping_cost}
TOTAL: KSh {total:,}

Thank you for your order! 🌱"""

    # URL encode the entire message
    encoded_message = quote(plain_message)
    whatsapp_url = f"https://wa.me/254726857007?text={encoded_message}"

    # Clear cart after order
    cart.clear()

    return JsonResponse({
        'success': True,
        'order_id': order.order_id,
        'whatsapp_url': whatsapp_url,
        'pdf_url': order.pdf_invoice.url if order.pdf_invoice else None
    })