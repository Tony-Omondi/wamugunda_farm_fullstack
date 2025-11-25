# cart/context_processors.py
def cart(request):
    return {'cart': getattr(request, 'cart', None)}