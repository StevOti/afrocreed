from .cart import Cart

# Context processor to add the cart to the context of all templates
def cart(request):
    return {'cart': Cart(request)}