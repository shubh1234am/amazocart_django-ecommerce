from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Contact, Product, Order, CartItem
from django.conf import settings
import razorpay

# Home page view
def index(request):
    products_by_category = []
    categories = Product.objects.values('category').distinct()

    for cat in categories:
        products = Product.objects.filter(category=cat['category'])
        if products.exists():
            products_by_category.append({
                'category': cat['category'],
                'products': products
            })

    context = {
        'products_by_category': products_by_category,
        'messages': messages.get_messages(request)
    }
    return render(request, 'index.html', context)

# About page view
def about(request):
    return render(request, "about.html")

# Contact page view with form handling
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Save contact details to the database
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        return render(request, "contact_success.html")
    return render(request, "contact.html")

# View single product details
def view_product(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'viewproduct.html', {'product': product})

# Checkout view
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('/auth/login/?next=/checkout/')

    # If POST request, process form submission
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        total_price = request.POST.get('amt')

        # Validate form inputs
        if not name or not email or not address1 or not city or not zip_code or not phone:
            messages.error(request, "All fields are required!")
            return redirect('checkout')

        # Save the order to the database
        new_order = Order.objects.create(
            user=request.user,
            name=name,
            email=email,
            address1=address1,
            city=city,
            zip_code=zip_code,
            phone=phone,
            total_price=total_price,
            status="Pending"
        )
        new_order.save()

        # Display a temporary alert message (flash message) for confirmation
        messages.success(request, f"Order placed successfully for {name}!")

        # Clear the user's cart after placing the order
        request.session['cart'] = {}

        # Redirect to order success page
        return redirect('order_success')

    # If GET request, display the checkout page
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product_name': product.product_name,
            'quantity': quantity,
            'price': float(product.price),
            'total_price': float(item_total)
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Checkout summary view
def checkout_summary(request):
    if not request.user.is_authenticated:
        return redirect('/auth/login/?next=/checkout-summary/')

    # Fetch cart data
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product_name': product.product_name,
            'quantity': quantity,
            'price': float(product.price),
            'total_price': float(item_total)
        })

    return render(request, 'checkout_summary.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Cart-related functionalities
def add_to_cart(request, product_id):
    if not Product.objects.filter(id=product_id).exists():
        return JsonResponse({'error': 'Invalid product ID'}, status=400)

    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    return JsonResponse({'cart_count': sum(cart.values())})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('cart')

def update_cart(request):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]
                try:
                    quantity = int(value)
                    if quantity > 0:
                        cart[product_id] = quantity
                    else:
                        del cart[product_id]
                except:
                    continue
        request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def cart_count(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'cart_count': sum(cart.values())})

# Order success page
def order_success(request):
    return render(request, 'order_success.html')







from django.shortcuts import render
from .models import Order

def payment_view(request):
    if request.method == "POST":
        try:
            amount_rupees = float(request.POST.get("amt", "0"))
            amount_paise = int(amount_rupees * 100)
            product_name = request.POST.get("product_name", "Your Amazing Product")

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": "1"
            })

            # ✅ **Save Order in Database with Razorpay Order ID**
            new_order = Order.objects.create(
                user=request.user,  # Ensure the user is authenticated
                name=request.user.username,
                email=request.user.email,
                razorpay_order_id=razorpay_order['id'],  # Store Razorpay Order ID properly
                total_price=amount_rupees,
                status="Pending"
            )

            context = {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': amount_paise,
                'order_id': razorpay_order['id'],  # Pass the order ID to the frontend
                'product_name': product_name
            }
            return render(request, 'payment.html', context)

        except Exception as e:
            print(f"Error creating Razorpay order: {e}")
            return render(request, 'payment_error.html', {'error': "Payment initialization failed."})

    else:
        return render(request, 'payment_form.html')

def payment_status(request, order_id):
    try:
        # Replace this with actual logic to check the payment status
        # For now, let's assume the payment is successful
        status = "success"  # Or "failed" based on actual payment status
        return JsonResponse({"status": status})

    except Exception as e:
        print(f"Error checking payment status for order {order_id}: {e}")
        return JsonResponse({"status": "failed"})

from django.shortcuts import redirect
from .models import Order

def payment_success(request):
    razorpay_order_id = request.GET.get('order_id', None)

    if razorpay_order_id:
        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        
        if order:
            order.status = "Paid"
            order.save()
            return redirect(f'/tracker/?order_id={order.id}')  # Redirect using correct order ID

    return redirect('/tracker/')



import json
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Order, OrderUpdate



def tracker(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/login')

    order_id = request.GET.get('order_id', None)  # Get specific order ID
    print(f"Received Order ID: {order_id}")  # Debugging print

    # ✅ Fetch only the requested order, ensuring it belongs to the user
    order = Order.objects.filter(id=order_id, user=request.user).first()

    if order:
        updates = OrderUpdate.objects.filter(order=order).order_by('-timestamp')  # Fetch updates for the order

        return render(request, 'myorder.html', {"order": order, "updates": updates})  # ✅ Pass updates too
    else:
        messages.warning(request, "Order not found.")
        return redirect('/myorder')
from django.utils.timezone import now
from .models import Order, OrderUpdate

def auto_update_order_status():
    orders = Order.objects.filter(status__in=["Processed", "Shipped"])

    for order in orders:
        if order.status == "Processed":
            order.status = "Shipped"
            OrderUpdate.objects.create(order=order, update_desc="Your order has been shipped!", timestamp=now())
        elif order.status == "Shipped":
            order.status = "Delivered"
            OrderUpdate.objects.create(order=order, update_desc="Your order has been delivered!", timestamp=now())

        order.save()
def myorder(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    for order in orders:
        order.updates = OrderUpdate.objects.filter(order=order).order_by('-timestamp')  # ✅ Ensures updates are passed

    return render(request, 'myorder.html', {"orders": orders})  # ✅ Fix: Pass updates properly
