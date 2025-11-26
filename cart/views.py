# cart/views.py — FINAL & PERFECT (NO WEASYPRINT, WORKS ON WINDOWS)
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
from cart.models import Order  # Your orders app

SHIPPING_ZONES = {
    'Thika Road': 250, 'Garden Estate': 250, 'Runda': 300, 'Muthaiga': 300,
    'Ruaka': 250, 'Thendegua': 250, 'Parklands': 250, 'Westlands': 250,
    'Redhill Road': 400, 'Sarit Center': 300, 'Waiyaki Way': 300,
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
    cart.remove(str(product_id))
    messages.success(request, 'Item removed.')
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
        messages.success(request, f"Delivery: {zone} (+KSh {SHIPPING_ZONES[zone]})")
    else:
        request.session.pop('shipping_zone', None)
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
    })

@require_POST
def create_whatsapp_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    selected_zone = request.session.get('shipping_zone', 'Not selected')
    shipping_cost = SHIPPING_ZONES.get(selected_zone, 0)
    total = cart.get_total_price() + shipping_cost

    # Save order
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

    # Generate PDF
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
    if pdf.err:
        return JsonResponse({'error': 'PDF generation failed'}, status=500)

    pdf_file = BytesIO(result.getvalue())
    order.pdf_invoice.save(f'invoice_{order.order_id}.pdf', File(pdf_file))
    order.save()

    # PERFECT WHATSAPP MESSAGE — EXACTLY WHAT YOU WANT
    items_text = "%0A".join([
        f"• {item['quantity']} × {item['product'].name} = KSh {item['total_price']}"
        for item in cart
    ])

    message = (
        f"*NEW ORDER #%23{order.order_id}*%0A%0A"
        f"Date: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}%0A%0A"
        f"*Items:*%0A{items_text}%0A%0A"
        f"*Delivery Zone:* {selected_zone}%0A"
        f"*Delivery Fee:* KSh {shipping_cost}%0A"
        f"*TOTAL:* KSh {total}%0A%0A"
        f"Invoice attached. Thank you!"
    )

    whatsapp_url = f"https://wa.me/254726857007?text={message}"

    return JsonResponse({
        'success': True,
        'order_id': order.order_id,
        'whatsapp_url': whatsapp_url,
        'pdf_url': order.pdf_invoice.url
    })