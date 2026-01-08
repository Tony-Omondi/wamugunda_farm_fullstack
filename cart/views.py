from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.files import File
from django.conf import settings
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from urllib.parse import quote

# --- IMPORTS ---
from shop.models import Product
from .cart import Cart
from .models import Order 

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

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart!',
            'cart_total': len(cart),
            'cart_price': float(cart.get_total_price())
        })

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

# --- ORDER CREATION LOGIC (UPDATED) ---
@require_POST
def create_whatsapp_order(request):
    cart = Cart(request)
    if len(cart) == 0:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # 1. Get Customer Details
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')

    if not full_name or not email or not phone:
        return JsonResponse({'error': 'Please fill in Name, Email, and Phone.'}, status=400)

    selected_zone = request.session.get('shipping_zone', 'Not selected')
    shipping_cost = SHIPPING_ZONES.get(selected_zone, 0)
    total = cart.get_total_price() + shipping_cost

    # 2. Save Order to Database
    order = Order.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
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

    # 3. Generate PDF Invoice
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
    
    pdf_content = result.getvalue()

    if not pdf.err:
        order.pdf_invoice.save(f'invoice_{order.order_id}.pdf', File(BytesIO(pdf_content)))
        order.save()

    # 4. Send Confirmation Email (To Customer AND Admin)
    try:
        subject = f"Order Confirmation - #{order.order_id} - Wamugunda Farm"
        body = f"""Dear {order.full_name},

Thank you for your order!

Order ID: {order.order_id}
Total Amount: KSh {total:,}
Delivery Zone: {selected_zone}

Your official invoice is attached to this email.

We are processing your order and will contact you shortly via WhatsApp/Phone for delivery.

Regards,
Wamugunda Farm Team
"""
        # --- NEW CODE: Admin Emails ---
        # This sends the email to the customer, but BCCs (Blind Copies) the admins
        admin_emails = [settings.EMAIL_HOST_USER, 'info.douglas@wamugundafarm.co.ke']

        email_msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],    # Sends to Customer
            bcc=admin_emails     # Sends Copy to Admins (Hidden from customer)
        )
        
        email_msg.attach(f'Invoice_{order.order_id}.pdf', pdf_content, 'application/pdf')
        
        # Changed to False so we can see errors in the console if it fails
        email_msg.send(fail_silently=False) 

    except Exception as e:
        print(f"Error sending email: {e}")

    # 5. Build WhatsApp Message
    items_text = "\n".join([
        f"• {item['quantity']} × {item['product'].name}"
        for item in cart
    ])

    plain_message = f"""*NEW ORDER #{order.order_id}*
👤 Name: {full_name}
📞 Phone: {phone}
✉️ Email: {email}

*Items:*
{items_text}

📍 Zone: {selected_zone}
🚚 Delivery: KSh {shipping_cost}
💰 *TOTAL: KSh {total:,}*

Thank you! 🌱"""

    encoded_message = quote(plain_message)
    whatsapp_url = f"https://wa.me/254715601620?text={encoded_message}"

    cart.clear()

    return JsonResponse({
        'success': True,
        'order_id': order.order_id,
        'whatsapp_url': whatsapp_url,
        'pdf_url': order.pdf_invoice.url if order.pdf_invoice else None
    })