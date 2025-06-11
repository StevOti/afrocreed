from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime

# Import some paypal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #Unique user id for the duplicate order

# Create your views here.

def payment_success(request):
    # Delete the browser cart
    # First get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants() 
    totals = cart.cart_total()

    # Clear the cart
    for key in list(request.session.keys()):
        if key == "session_key":
            # delete the session key
            del request.session[key]

    return render(request, 'payment/payment_success.html', {})


def payment_failed(request):
    # Render the payment success template
    return render(request, 'payment/payment_failed.html', {})

def checkout(request):
    # Render the checkout template
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants() 
    totals = cart.cart_total()

    if request.user.is_authenticated:
        
        # Shipping User
        Shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # Checkout as logged-in user
        # Shipping form
        shipping_form = ShippingForm(request.POST or None, instance=Shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form})


def billing_info(request):

    if request.POST:
        # Get cart 
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants() 
        totals = cart.cart_total()

        # Create a session for the shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Create shipping address from the session data
        shipping_address = f"{my_shipping['shipping_full_name']}\n {my_shipping['shipping_address1']}\n {my_shipping['shipping_address2']}\n {my_shipping['shipping_city']}\n {my_shipping['shipping_state']}\n {my_shipping['shipping_zipcode']}\n {my_shipping['shipping_country']}"
        amount_paid = totals

        # Get the host
        host = request.get_host()

        # Create an invoice number
        my_Invoice = str(uuid.uuid4())

        # Create an order

        # Create paypal form dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Order from AfroCreed',
            'no_shipping': 2,
            'invoice': my_Invoice,  # Unique invoice ID
            'currency_code': 'USD',
            'notify_url': f'https://{host}{reverse("paypal-ipn")}',  # IPN URL
            'return': f'https://{host}{reverse("payment_success")}',  # Return URL after payment
            'cancel_return': f'https://{host}{reverse("payment_failed")}',  # Cancel URL

            # after hosting change all the urls to https
            # 'notify_url': f'https://{host}{reverse("paypal-ipn")}',  # IPN URL
            # 'return': f'https://{host}{reverse("payment_success")}',  # Return URL after payment
            # 'cancel_return': f'https://{host}{reverse("home")}',  # Cancel URL

        }

        paypal_form = PayPalPaymentsForm(initial=paypal_dict)



        # check to see if user is logged in
        if request.user.is_authenticated:
            # Get payment form
            billing_form = PaymentForm()


            # Logged in user
            user = request.user

            # Create order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()


            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products:
                # Get product id
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get product quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price, user=user)
                        create_order_item.save()

            # Clear the cart from database
            current_user = Profile.objects.filter(user__id=request.user.id)

            # Delete shopping cart from database
            current_user.update(old_cart="")

            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form, 'paypal_form':paypal_form})
        else:
            # not logged in
            # Create order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()

            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products:
                # Get product id
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get product quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            
            # Get payment form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form})

    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')
    

def process_order(request):
    if request.POST:
        # Get cart 
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants() 
        totals = cart.cart_total()



        # Get billing info from the billing info page
        payment_form = PaymentForm(request.POST or None)
        # Get shipping session data
        my_shipping = request.session.get('my_shipping')
        
        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Create shipping address from the session data
        shipping_address = f"{my_shipping['shipping_full_name']}\n {my_shipping['shipping_address1']}\n {my_shipping['shipping_address2']}\n {my_shipping['shipping_city']}\n {my_shipping['shipping_state']}\n {my_shipping['shipping_zipcode']}\n {my_shipping['shipping_country']}"
        amount_paid = totals


        # Create an order
        if request.user.is_authenticated:
            # Logged in user
            user = request.user

            # Create order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()


            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products:
                # Get product id
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get product quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price, user=user)
                        create_order_item.save()

            # Clear the cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # delete the session key
                    del request.session[key]

            # Clear the cart from database
            current_user = Profile.objects.filter(user__id=request.user.id)

            # Delete shopping cart from database
            current_user.update(old_cart="")

            messages.success(request, 'Order Placed!')
            return redirect('home')
        else:
            # not logged in
            # Create order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            # Get the order id
            order_id = create_order.pk
            # Get product info
            for product in cart_products:
                # Get product id
                product_id = product.id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get product quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
             # Clear the cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # delete the session key
                    del request.session[key]

            messages.success(request, 'Order Placed!')
            return redirect('home')
        
    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')
    

def shipped_dash(request):

    # Check if user is logged in
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            # Get the order
            order = Order.objects.filter(id=num)
            
            # Grab date and time
            now = datetime.datetime.now()
            # Update shipping status
            order.update(shipped=False)  
            messages.success(request, 'Shipping status Updated!')
            return redirect('home')
        
        return render(request, 'payment/shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']

            # Get the order
            order = Order.objects.filter(id=num)
            
            # Grab date and time
            now = datetime.datetime.now()
            # Update shipping status
            order.update(shipped=True, date_shipped=now)  
            messages.success(request, 'Shipping status Updated!')
            return redirect('home')
        
        return render(request, 'payment/not_shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')
    

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == "true":
                # Get the orders
                order = Order.objects.filter(id=pk)
                # Update the order status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
                
            else:
                # Get the orders
                order = Order.objects.filter(id=pk)
                # Update the order status
                order.update(shipped=False)
            
            messages.success(request, 'Shipping status Updated!')
            return redirect('home')
                

        return render(request, 'payment/orders.html', {'order': order, 'items': items})

    else:
        messages.success(request, 'Access Denied!')
        return redirect('home')