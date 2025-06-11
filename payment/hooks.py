from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from . models import Order

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Add ten second delay to allow for the IPN to be processed
    time.sleep(10)
    # Grab the info that paypal sends
    paypal_obj = sender

    # Grab the invoice
    my_Invoice = str(paypal_obj.invoice)

    # Match the paypal invoice to the order
    # Look up the order
    my_Order = Order.objects.get(invoice=my_Invoice)

    # Record that the order has been paid
    my_Order.paid = True
    # Save the order
    my_Order.save()




    # print(paypal_obj)
    # print(f'Amount Paid: {paypal_obj.mc_gross}')