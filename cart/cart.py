from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get request
        self.request = request

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the session key doesn't exist, create a new one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        # If the session key exists, use it to initialize the cart in all the pages
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        # Check if the product is already in the cart
        if product_id in self.cart:
            self.cart[product_id] = int(quantity)
        else:
            self.cart[product_id] = int(product_qty)

        # Save the session
        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'", '\"')
            # save carty to the profile model 
            current_user.update(old_cart=str (carty))


    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        # Get the products from the db using the ids
        products = Product.objects.filter(id__in=product_ids)

        # Return the products
        return products
    
    def get_quants(self):
        # Get the quantities of the products in the cart
        quantities = self.cart
        # Return the quantities
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product.id)
        product_qty = int(quantity)

        # Get cart 
        ourcart = self.cart

        # Update cart
        ourcart[product_id] = product_qty

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'", '\"')
            # save carty to the profile model 
            current_user.update(old_cart=str (carty))

        thing = self.cart    
        return thing
    
    def delete(self, product):
        product_id = str(product)

        # delete from cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'", '\"')
            # save carty to the profile model 
            current_user.update(old_cart=str (carty))



    def cart_total(self):
        # Get products ids from cart
        product_ids = self.cart.keys()
        # Get the products from the db using the ids
        products = Product.objects.filter(id__in=product_ids)
        # Get the quantities of the products in the cart
        quantities = self.cart

        # Get the total price of the products in the cart
        total = 0

        for key, value in quantities.items():
            key = int(key)
            
            for product in products:
                if product.id == key:

                    if product.is_sale:
                        total = total + (product.sale_price * value)

                    else:
                        total = total + (product.price * value)

        # Return the total price
        return total
    
    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        # Check if the product is already in the cart
        if product_id in self.cart:
            self.cart[product_id] = int(quantity)
        else:
            self.cart[product_id] = int(product_qty)

        # Save the session
        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'", '\"')
            # save carty to the profile model 
            current_user.update(old_cart=str (carty))