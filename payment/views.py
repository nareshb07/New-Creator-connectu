from django.shortcuts import render
from django.conf import settings 
# Create your views here.
import razorpay
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    # ...
def payment_request(request):
    
    response = client.order.create({
    'amount': 50000,  # Amount in paise (e.g., ₹500 = 50000 paise)
    'currency': 'INR',
    'payment_capture': '1'  # Auto-capture payments after successful redirection
})
    
    order_id = response['id']
    api_key = "rzp_test_JXDhWdMqazVxVV"


    return render(request, 'payment_form.html', {'order_id': order_id, 'api_key':api_key})
